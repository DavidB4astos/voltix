import asyncio
import io
import unittest
import urllib.error
from types import SimpleNamespace, MethodType
from unittest.mock import AsyncMock, patch

from voltix.internal_customers import (customer_record, customer_page, query_parameters,
    bounded_read, customer_date_display, history_parameters, order_history_page, order_record,
    customer_update_payload, customer_status_payload)
import voltix.voltix as app


def record(**extra):
    value = dict(id=1, nome_completo="Cliente fictício", email_masked="mar*****",
                 telefone_masked="*****1234", status="ATIVO", created_at=1)
    value.update(extra)
    return value


def order_item(**extra):
    value = dict(variacao_id=11, sku="SKU-1", nome_ou_descricao="Camiseta",
                 quantidade=2, preco_unitario="49.90", subtotal="99.80")
    value.update(extra)
    return value


def order(**extra):
    value = dict(id=1, codigo="PED-1", data_pedido=1704067200000, status="ENTREGUE",
                 subtotal="99.80", valor_frete="10.00", valor_total="109.80",
                 itens=[order_item()])
    value.update(extra)
    return value


def history_payload(**extra):
    value = dict(cliente_id=42, items=[order()], page=1, per_page=20,
                 total_items=1, total_pages=1)
    value.update(extra)
    return value


class CustomerContractTests(unittest.TestCase):
    def test_customer_date_has_explicit_timezone_and_accepts_iso(self):
        expected = "01/01/2024 às 00:00 (UTC)"
        for value in [1704067200000, "1704067200000", "2023-12-31T21:00:00-03:00"]:
            self.assertEqual(customer_date_display(value), expected)

    def test_unusable_date_does_not_break_customer_detail(self):
        for value in ["", "invalid", 10**100]:
            self.assertEqual(customer_date_display(value), "Data indisponível")

    def test_rejects_raw_and_unexpected_sensitive_fields(self):
        for extra in [{"email": "private@example.test"}, {"password": "secret"}, {"USER_ID": 2}]:
            with self.assertRaises(ValueError): customer_record(record(**extra))
        for field, raw in [("email_masked", "private@example.test"), ("telefone_masked", "11999991234"), ("cpf_masked", "12345678909")]:
            value = record(cpf_masked="***.***.***-09")
            value[field] = raw
            with self.assertRaises(ValueError): customer_record(value, detail=True)

    def test_masks_null_and_short_values_are_safe(self):
        for email in ["a*****", "*****", None]:
            value = record(); value["email_masked"] = email
            self.assertNotIn("@", customer_record(value).email_masked)

    def test_detail_requires_exact_schema_and_id(self):
        self.assertEqual(customer_record(record(cpf_masked="***.***.***-09"), detail=True).cpf_masked, "***.***.***-09")
        with self.assertRaises(ValueError): customer_record(record(), detail=True)
        value = record(); value["id"] = True
        with self.assertRaises(ValueError): customer_record(value)

    def test_query_normalization_and_invalid_inputs(self):
        self.assertEqual(query_parameters("  mouse  ", "ATIVO", 1)["q"], "mouse")
        for q, status, page, size in [("x"*101,"ATIVO",1,20),("","ANY",1,20),("","ATIVO",0,20),("","ATIVO",True,20),("","ATIVO",1,51)]:
            with self.assertRaises(ValueError): query_parameters(q,status,page,size)

    def test_page_contract_and_empty_beyond_end(self):
        payload=dict(items=[record()],page=1,per_page=20,total_items=1,total_pages=1)
        self.assertEqual(customer_page(payload,page=1)[1:], (1,1))
        payload.update(items=[],page=2)
        self.assertEqual(customer_page(payload,page=2)[0], [])
        payload.update(total_items=0,total_pages=0)
        self.assertEqual(customer_page(payload,page=2)[1:], (0,0))
        payload["total_pages"] = 1
        with self.assertRaises(ValueError): customer_page(payload,page=2)

    def test_history_parameters_defaults_dates_and_normalization(self):
        self.assertEqual(history_parameters("TODOS", "", "", 1),
                         {"status": "TODOS", "page": 1, "per_page": 20})
        self.assertEqual(history_parameters("ENTREGUE", " 2026-10-01 ", "2026-10-31", 2),
                         {"status": "ENTREGUE", "page": 2, "per_page": 20,
                          "from": "2026-10-01", "to": "2026-10-31"})
        self.assertEqual(history_parameters("TODOS", None, "", 1, 50)["per_page"], 50)

    def test_history_parameters_reject_invalid_values(self):
        for status, start, end, page, size in [
                ("PAGO", "", "", 1, 20), ("TODOS", "2026-2-01", "", 1, 20),
                ("TODOS", "2026-02-31", "", 1, 20), ("TODOS", "2026-10-31", "2026-10-01", 1, 20),
                ("TODOS", "", "", 0, 20), ("TODOS", "", "", True, 20),
                ("TODOS", "", "", 1, 51)]:
            with self.assertRaises(ValueError):
                history_parameters(status, start, end, page, size)

    def test_order_record_preserves_persisted_values(self):
        record_value = order_record(order())
        self.assertEqual((record_value.id, record_value.status, record_value.valor_total),
                         (1, "ENTREGUE", "109.80"))
        self.assertEqual(record_value.data_pedido_display, "01/01/2024 às 00:00 (UTC)")
        self.assertEqual(record_value.itens[0].subtotal, "99.80")

    def test_order_record_prefers_table_without_mutating_values(self):
        value = order(subtotal=10, valor_frete=0, valor_total=10)
        parsed = order_record(value)
        self.assertEqual((parsed.subtotal, parsed.valor_frete, parsed.valor_total),
                         ("10", "0", "10"))
        empty_sku = order(itens=[order_item(sku=None, nome_ou_descricao=None)])
        self.assertEqual(order_record(empty_sku).itens[0].sku, "")
        self.assertEqual(order_record(empty_sku).itens[0].nome_ou_descricao, "")

    def test_order_record_rejects_unexpected_or_invalid_fields(self):
        for value in [order(extra=1), order(status="PAGO"), order(itens={}),
                      order(subtotal=True), order(subtotal="1e3"),
                      order(itens=[order_item(extra=1)]), order(itens=[order_item(quantidade=0)]),
                      order(itens=[order_item(variacao_id=True)]), order(codigo="")]:
            with self.assertRaises(ValueError):
                order_record(value)

    def test_order_history_page_contract_and_empty_page(self):
        items, total, pages = order_history_page(history_payload(), customer_id=42, page=1)
        self.assertEqual((len(items), total, pages), (1, 1, 1))
        empty = history_payload(items=[], total_items=0, total_pages=0, page=2)
        self.assertEqual(order_history_page(empty, customer_id=42, page=2)[1:], (0, 0))
        for value in [history_payload(cliente_id=41), history_payload(page=2),
                      history_payload(total_pages=2), history_payload(extra=1),
                      history_payload(items=[order()], total_items=2, total_pages=1),
                      history_payload(items=[order(), order()])]:
            with self.assertRaises(ValueError):
                order_history_page(value, customer_id=42, page=1)

    def test_order_history_rejects_duplicate_orders(self):
        value = history_payload(items=[order(), order()], total_items=2, total_pages=1)
        with self.assertRaises(ValueError):
            order_history_page(value, customer_id=42, page=1)

    def test_customer_update_payload_normalizes_and_keeps_blank_fields(self):
        self.assertEqual(customer_update_payload("  ", "", " ", current_name="Atual"), {})
        self.assertEqual(
            customer_update_payload(" Atual ", " MARIA@Example.TEST ", " 1199999 ",
                                    current_name="Atual"),
            {"email": "maria@example.test", "telefone": "1199999"})
        self.assertEqual(customer_update_payload(" Novo Nome ", "", "", current_name="Atual"),
                         {"nome_completo": "Novo Nome"})

    def test_customer_update_payload_rejects_invalid_values(self):
        cases = [("x" * 301, "", ""), ("", "invalido", ""), ("", "a" * 250 + "@x.test", ""),
                 ("", "", "1" * 31), (None, "", "")]
        for name, mail, phone in cases:
            with self.assertRaises(ValueError):
                customer_update_payload(name, mail, phone, current_name="Atual")

    def test_customer_status_payload_accepts_only_known_status(self):
        self.assertEqual(customer_status_payload("INATIVO"), {"status": "INATIVO"})
        self.assertEqual(customer_status_payload("ATIVO"), {"status": "ATIVO"})
        for value in ["", "TODOS", "ativo", None]:
            with self.assertRaises(ValueError):
                customer_status_payload(value)


class CustomerWorkflowTests(unittest.IsolatedAsyncioTestCase):
    def state(self, role="FUNCIONARIO"):
        state=SimpleNamespace(_auth_token="internal-fixture",is_authenticated=True,session_status="success",
            user_status="ATIVO",user_role=role,user_id=9, internal_customers_search="",internal_customers_status="ATIVO",
            internal_customers_page=1,_internal_customers_generation=0,_internal_detail_generation=0,
            internal_customers=[],internal_customer_detail=[],internal_customers_loading=False,
            internal_customer_loading=False,internal_customers_message="",internal_customers_total=0,internal_customers_pages=0,
            internal_customer_edit_nome="",internal_customer_edit_email="",internal_customer_edit_telefone="",
            internal_customer_status_confirmation=False,internal_customer_saving=False,
            internal_customer_feedback="",internal_customer_feedback_error=False,
            internal_customer_history=[],internal_customer_history_customer_id=0,
            internal_customer_history_status="TODOS",internal_customer_history_from="",internal_customer_history_to="",
            internal_customer_history_status_input="TODOS",internal_customer_history_from_input="",internal_customer_history_to_input="",
            internal_customer_history_page=1,internal_customer_history_total=0,internal_customer_history_pages=0,
            internal_customer_history_loading=False,internal_customer_history_message="",_internal_history_generation=0)
        for method in ["_internal_customer_allowed","_internal_customer_admin_allowed",
                       "_clear_internal_customers","_clear_internal_customer_history",
                       "_clear_internal_customer_edit","_customer_feedback",
                       "_load_internal_customers","_submit_internal_customer_update"]:
            setattr(state,method,MethodType(getattr(app.State,method),state))
        state.close_internal_customer=MethodType(app.State.close_internal_customer.fn,state)
        def clear(message):
            state._clear_internal_customers();state._auth_token="";state.is_authenticated=False
        state._clear_authentication_state=clear
        return state

    async def test_both_roles_use_internal_token_only(self):
        for role in ["FUNCIONARIO","ADMINISTRADOR"]:
            state=self.state(role)
            payload=dict(items=[record()],page=1,per_page=20,total_items=1,total_pages=1)
            with patch.object(app,"_required_environment_url",return_value="https://example.test/customers"), patch.object(app,"_server_side_xano_request",AsyncMock(return_value=payload)) as request:
                await app.State.load_internal_customers.fn(state)
            self.assertEqual(state.internal_customers_total,1)
            self.assertEqual(request.await_args.kwargs["authorization"],"Bearer internal-fixture")
            self.assertFalse(request.await_args.kwargs["retry_rate_limit"])

    async def test_customer_and_inactive_sessions_never_request(self):
        for role,status in [("CLIENTE","ATIVO"),("FUNCIONARIO","INATIVO")]:
            state=self.state(role);state.user_status=status
            with patch.object(app,"_server_side_xano_request",AsyncMock()) as request:
                await app.State.load_internal_customers.fn(state)
            request.assert_not_awaited()

    async def test_logout_during_read_discards_result(self):
        state=self.state()
        async def request(*args,**kwargs):
            state._clear_authentication_state("logout")
            return dict(items=[record()],page=1,per_page=20,total_items=1,total_pages=1)
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers"), patch.object(app,"_server_side_xano_request",side_effect=request):
            await app.State.load_internal_customers.fn(state)
        self.assertEqual(state.internal_customers,[])

    async def test_unauthorized_clears_existing_data(self):
        state=self.state();state.internal_customer_detail=[customer_record(record())]
        error=urllib.error.HTTPError("https://example.test",403,"forbidden",{},io.BytesIO())
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers"), patch.object(app,"_server_side_xano_request",AsyncMock(side_effect=error)):
            await app.State.load_internal_customers.fn(state)
        self.assertFalse(state.is_authenticated);self.assertEqual(state.internal_customer_detail,[])

    async def test_detail_wrong_customer_is_rejected(self):
        state=self.state()
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",AsyncMock(return_value=record(cpf_masked="***.***.***-09"))):
            await app.State.show_internal_customer.fn(state,2)
        self.assertEqual(state.internal_customer_detail,[])

    async def test_filter_generation_discards_previous_list(self):
        state=self.state()
        async def request(*args,**kwargs):
            state._internal_customers_generation += 1
            return dict(items=[record()],page=1,per_page=20,total_items=1,total_pages=1)
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers"), patch.object(app,"_server_side_xano_request",side_effect=request):
            await app.State.load_internal_customers.fn(state)
        self.assertEqual(state.internal_customers,[])

    async def test_close_discards_detail_in_flight(self):
        state=self.state()
        async def request(*args,**kwargs):
            state.close_internal_customer()
            return record(cpf_masked="***.***.***-09")
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",side_effect=request):
            await app.State.show_internal_customer.fn(state,1)
        self.assertEqual(state.internal_customer_detail,[])

    async def test_clear_resets_form_and_sensitive_state(self):
        state=self.state();state.internal_customers_search_input="anterior";state.internal_customers_status_input="TODOS"
        state.internal_customers_page=3;state.internal_customer_detail=[customer_record(record())]
        app.State.clear_internal_customer_filters.fn(state)
        self.assertEqual((state.internal_customers_page,state.internal_customers_search_input,state.internal_customers_status_input),(1,"","ATIVO"))
        self.assertEqual(state.internal_customer_detail,[])

    def history_state(self, customer_id=42):
        state=self.state()
        state.internal_customer_history_customer_id=customer_id
        state.internal_customer_detail=[customer_record(record(id=customer_id))]
        return state

    async def test_history_uses_orders_url_and_internal_token(self):
        state=self.history_state()
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}/orders"), patch.object(app,"_server_side_xano_request",AsyncMock(return_value=history_payload())) as request:
            await app.State.load_internal_customer_history.fn(state)
        self.assertEqual(state.internal_customer_history_total,1)
        url=request.await_args.args[0]
        self.assertIn("/customers/42/orders?",url)
        self.assertIn("status=TODOS",url)
        self.assertIn("page=1",url)
        self.assertEqual(request.await_args.kwargs["authorization"],"Bearer internal-fixture")
        self.assertFalse(request.await_args.kwargs["retry_rate_limit"])

    async def test_history_invalid_filters_never_request(self):
        state=self.history_state();state.internal_customer_history_status="PAGO"
        with patch.object(app,"_server_side_xano_request",AsyncMock()) as request:
            await app.State.load_internal_customer_history.fn(state)
        request.assert_not_awaited()
        self.assertIn("Filtros inválidos",state.internal_customer_history_message)

    async def test_history_wrong_customer_response_is_rejected(self):
        state=self.history_state()
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}/orders"), patch.object(app,"_server_side_xano_request",AsyncMock(return_value=history_payload(cliente_id=41))):
            await app.State.load_internal_customer_history.fn(state)
        self.assertEqual(state.internal_customer_history,[])
        self.assertIn("Histórico indisponível",state.internal_customer_history_message)

    async def test_history_logout_discards_result(self):
        state=self.history_state()
        async def request(*args,**kwargs):
            state._clear_authentication_state("logout")
            return history_payload()
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}/orders"), patch.object(app,"_server_side_xano_request",side_effect=request):
            await app.State.load_internal_customer_history.fn(state)
        self.assertEqual(state.internal_customer_history,[])

    async def test_history_unauthorized_clears_customer_and_history(self):
        state=self.history_state()
        error=urllib.error.HTTPError("https://example.test",403,"forbidden",{},io.BytesIO())
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}/orders"), patch.object(app,"_server_side_xano_request",AsyncMock(side_effect=error)):
            await app.State.load_internal_customer_history.fn(state)
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.internal_customer_history,[])
        self.assertEqual(state.internal_customer_detail,[])

    async def test_apply_history_filters_resets_page_and_commits_values(self):
        state=self.history_state();state.internal_customer_history_page=3
        app.State.apply_internal_customer_history_filters.fn(state,{"status":"ENTREGUE","from":"2026-10-01","to":"2026-10-31"})
        self.assertEqual((state.internal_customer_history_status,state.internal_customer_history_from,
            state.internal_customer_history_to,state.internal_customer_history_page),
            ("ENTREGUE","2026-10-01","2026-10-31",1))

    async def test_invalid_history_filters_keep_previous_values(self):
        state=self.history_state();state.internal_customer_history_status="ENTREGUE"
        state.internal_customer_history_page=2
        app.State.apply_internal_customer_history_filters.fn(state,{"status":"ENTREGUE","from":"2026-10-31","to":"2026-10-01"})
        self.assertEqual((state.internal_customer_history_status,state.internal_customer_history_page),
                         ("ENTREGUE",2))
        self.assertIn("Filtros inválidos",state.internal_customer_history_message)

    async def test_clear_history_filters_restores_defaults(self):
        state=self.history_state();state.internal_customer_history_status="ENTREGUE"
        state.internal_customer_history_from="2026-10-01";state.internal_customer_history_to="2026-10-31"
        state.internal_customer_history_page=2
        app.State.clear_internal_customer_history_filters.fn(state)
        self.assertEqual((state.internal_customer_history_status,state.internal_customer_history_from,
            state.internal_customer_history_to,state.internal_customer_history_page),
            ("TODOS","","",1))

    async def test_history_pagination_is_bounded(self):
        state=self.history_state();state.internal_customer_history_pages=2
        app.State.internal_customer_history_next.fn(state)
        self.assertEqual(state.internal_customer_history_page,2)
        app.State.internal_customer_history_next.fn(state)
        self.assertEqual(state.internal_customer_history_page,2)
        app.State.internal_customer_history_previous.fn(state)
        self.assertEqual(state.internal_customer_history_page,1)
        app.State.internal_customer_history_previous.fn(state)
        self.assertEqual(state.internal_customer_history_page,1)
        state.internal_customer_history_loading=True
        app.State.internal_customer_history_next.fn(state)
        self.assertEqual(state.internal_customer_history_page,1)

    async def test_show_customer_prepares_history_and_close_clears_it(self):
        state=self.state()
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",AsyncMock(return_value=record(cpf_masked="***.***.***-09"))):
            await app.State.show_internal_customer.fn(state,1)
        self.assertEqual(state.internal_customer_history_customer_id,1)
        self.assertEqual(state.internal_customer_history_status,"TODOS")
        state.internal_customer_history=[order_record(order())];state.internal_customer_history_total=1
        state.internal_customer_history_pages=1
        state.close_internal_customer()
        self.assertEqual(state.internal_customer_history,[])
        self.assertEqual(state.internal_customer_history_customer_id,0)
        self.assertEqual(state.internal_customer_history_total,0)

    async def test_rate_limit_is_bounded_and_auth_never_retries(self):
        error=lambda code,delay:urllib.error.HTTPError("https://example.test",code,"error",{"Retry-After":delay},io.BytesIO())
        sleep=AsyncMock();request=AsyncMock(side_effect=[error(429,"1"),{"ok":True}])
        self.assertEqual(await bounded_read(request,sleep=sleep),{"ok":True});sleep.assert_awaited_once_with(1)
        for code,delay in [(429,"31"),(429,"nan"),(429,""),(403,"1"),(401,"0")]:
            request=AsyncMock(side_effect=error(code,delay))
            with self.assertRaises(urllib.error.HTTPError): await bounded_read(request,sleep=AsyncMock())
            self.assertEqual(request.await_count,1)
        request=AsyncMock(side_effect=error(429,"0"))
        with self.assertRaises(urllib.error.HTTPError): await bounded_read(request,sleep=AsyncMock())
        self.assertEqual(request.await_count,2)

    async def test_show_customer_prepares_administrator_edit_fields(self):
        state=self.state("ADMINISTRADOR")
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",AsyncMock(return_value=record(cpf_masked="***.***.***-09"))):
            await app.State.show_internal_customer.fn(state,1)
        self.assertEqual(state.internal_customer_edit_nome,"Cliente fictício")
        self.assertEqual(state.internal_customer_edit_email,"")
        self.assertEqual(state.internal_customer_edit_telefone,"")
        self.assertFalse(state.internal_customer_status_confirmation)

    async def test_administrator_updates_customer_and_refreshes_list(self):
        state=self.state("ADMINISTRADOR")
        state.internal_customer_detail=[customer_record(record(cpf_masked="***.***.***-09"),detail=True)]
        updated=record(nome_completo="Novo Nome",cpf_masked="***.***.***-09")
        page=dict(items=[record(nome_completo="Novo Nome")],page=1,per_page=20,total_items=1,total_pages=1)
        async def request(*args,**kwargs):
            return updated if kwargs.get("method")=="PATCH" else page
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",side_effect=request) as call:
            await app.State.save_internal_customer.fn(state,{"nome_completo":"Novo Nome","email":"","telefone":""})
        first=call.await_args_list[0]
        self.assertEqual(first.args[0],"https://example.test/customers/1")
        self.assertEqual(first.kwargs["method"],"PATCH")
        self.assertEqual(first.kwargs["payload"],{"nome_completo":"Novo Nome"})
        self.assertEqual(first.kwargs["authorization"],"Bearer internal-fixture")
        self.assertFalse(first.kwargs["retry_rate_limit"])
        self.assertEqual(state.internal_customer_detail[0].nome_completo,"Novo Nome")
        self.assertEqual(state.internal_customers_total,1)
        self.assertIn("atualizado",state.internal_customer_feedback)
        self.assertFalse(state.internal_customer_feedback_error)

    async def test_employee_cannot_update_customer(self):
        state=self.state("FUNCIONARIO")
        state.internal_customer_detail=[customer_record(record(cpf_masked="***.***.***-09"),detail=True)]
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",AsyncMock()) as request:
            await app.State.save_internal_customer.fn(state,{"nome_completo":"Novo","email":"","telefone":""})
        request.assert_not_awaited()
        self.assertTrue(state.internal_customer_feedback_error)
        self.assertIn("administrador",state.internal_customer_feedback)

    async def test_empty_or_unchanged_update_does_not_request(self):
        state=self.state("ADMINISTRADOR")
        state.internal_customer_detail=[customer_record(record(cpf_masked="***.***.***-09"),detail=True)]
        for form in [{"nome_completo":"Cliente fictício","email":"","telefone":""},
                     {"nome_completo":"","email":"","telefone":""}]:
            with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",AsyncMock()) as request:
                await app.State.save_internal_customer.fn(state,form)
            request.assert_not_awaited()
            self.assertTrue(state.internal_customer_feedback_error)

    async def test_inactivation_requires_confirmation_then_patches_status(self):
        state=self.state("ADMINISTRADOR")
        state.internal_customer_detail=[customer_record(record(cpf_masked="***.***.***-09"),detail=True)]
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",AsyncMock()) as request:
            await app.State.request_internal_customer_status_change.fn(state,"INATIVO")
        request.assert_not_awaited()
        self.assertTrue(state.internal_customer_status_confirmation)
        inactive=record(status="INATIVO",cpf_masked="***.***.***-09")
        empty_page=dict(items=[],page=1,per_page=20,total_items=0,total_pages=0)
        async def request_status(*args,**kwargs):
            return inactive if kwargs.get("method")=="PATCH" else empty_page
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",side_effect=request_status) as call:
            await app.State.confirm_internal_customer_status_change.fn(state)
        self.assertEqual(call.await_args_list[0].kwargs["payload"],{"status":"INATIVO"})
        self.assertEqual(state.internal_customer_detail[0].status,"INATIVO")
        self.assertFalse(state.internal_customer_status_confirmation)
        self.assertIn("inativado",state.internal_customer_feedback)

    async def test_cancel_and_reactivation_flow(self):
        state=self.state("ADMINISTRADOR")
        state.internal_customer_detail=[customer_record(record(status="INATIVO",cpf_masked="***.***.***-09"),detail=True)]
        state.internal_customer_status_confirmation=True
        app.State.cancel_internal_customer_status_change.fn(state)
        self.assertFalse(state.internal_customer_status_confirmation)
        self.assertEqual(state.internal_customer_feedback,"")
        active=record(cpf_masked="***.***.***-09")
        empty_page=dict(items=[],page=1,per_page=20,total_items=0,total_pages=0)
        async def request(*args,**kwargs):
            return active if kwargs.get("method")=="PATCH" else empty_page
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",side_effect=request) as call:
            await app.State.request_internal_customer_status_change.fn(state,"ATIVO")
        self.assertEqual(call.await_args_list[0].kwargs["payload"],{"status":"ATIVO"})
        self.assertEqual(state.internal_customer_detail[0].status,"ATIVO")
        self.assertIn("reativado",state.internal_customer_feedback)

    async def test_duplicate_email_is_reported_without_changing_detail(self):
        state=self.state("ADMINISTRADOR")
        state.internal_customer_detail=[customer_record(record(cpf_masked="***.***.***-09"),detail=True)]
        error=urllib.error.HTTPError("https://example.test",400,"bad request",{},io.BytesIO())
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",AsyncMock(side_effect=error)):
            await app.State.save_internal_customer.fn(state,{"nome_completo":"","email":"dup@example.test","telefone":""})
        self.assertEqual(state.internal_customer_detail[0].nome_completo,"Cliente fictício")
        self.assertTrue(state.internal_customer_feedback_error)
        self.assertIn("e-mail",state.internal_customer_feedback)

    async def test_update_unauthorized_clears_session_and_discards_logout_result(self):
        state=self.state("ADMINISTRADOR")
        state.internal_customer_detail=[customer_record(record(cpf_masked="***.***.***-09"),detail=True)]
        error=urllib.error.HTTPError("https://example.test",403,"forbidden",{},io.BytesIO())
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",AsyncMock(side_effect=error)):
            await app.State.save_internal_customer.fn(state,{"nome_completo":"Novo","email":"","telefone":""})
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.internal_customer_detail,[])

        state=self.state("ADMINISTRADOR")
        state.internal_customer_detail=[customer_record(record(cpf_masked="***.***.***-09"),detail=True)]
        updated=record(nome_completo="Novo Nome",cpf_masked="***.***.***-09")
        async def request(*args,**kwargs):
            state._clear_authentication_state("logout")
            return updated
        with patch.object(app,"_required_environment_url",return_value="https://example.test/customers/{customer_id}"), patch.object(app,"_server_side_xano_request",side_effect=request):
            await app.State.save_internal_customer.fn(state,{"nome_completo":"Novo Nome","email":"","telefone":""})
        self.assertEqual(state.internal_customer_detail,[])
        self.assertEqual(state.internal_customer_feedback,"")
