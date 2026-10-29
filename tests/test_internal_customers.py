import asyncio
import io
import unittest
import urllib.error
from types import SimpleNamespace, MethodType
from unittest.mock import AsyncMock, patch

from voltix.internal_customers import customer_record, customer_page, query_parameters, bounded_read
import voltix.voltix as app


def record(**extra):
    return dict(id=1, nome_completo="Cliente fictício", email_masked="mar*****",
                telefone_masked="*****1234", status="ATIVO", created_at=1, **extra)


class CustomerContractTests(unittest.TestCase):
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


class CustomerWorkflowTests(unittest.IsolatedAsyncioTestCase):
    def state(self, role="FUNCIONARIO"):
        state=SimpleNamespace(_auth_token="internal-fixture",is_authenticated=True,session_status="success",
            user_status="ATIVO",user_role=role,user_id=9, internal_customers_search="",internal_customers_status="ATIVO",
            internal_customers_page=1,_internal_customers_generation=0,_internal_detail_generation=0,
            internal_customers=[],internal_customer_detail=[],internal_customers_loading=False,
            internal_customer_loading=False,internal_customers_message="",internal_customers_total=0,internal_customers_pages=0)
        for method in ["_internal_customer_allowed","_clear_internal_customers"]:
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
