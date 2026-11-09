import io
import unittest
import urllib.error
from types import MethodType, SimpleNamespace
from unittest.mock import AsyncMock, patch

from voltix.internal_orders import (order_detail, order_filters,
    order_status_result, order_summary_page, order_summary_record)
import voltix.voltix as app


def item(**extra):
    value = dict(variacao_id=11, sku="SKU-1", nome_ou_descricao="Produto",
                 quantidade=1, preco_unitario="10.00", subtotal="10.00")
    value.update(extra)
    return value


def summary(**extra):
    value = dict(
        id=1, codigo="PED-1", data_pedido=1704067200000, status="PAGAMENTO_CONFIRMADO",
        cliente={"id": 42, "nome_completo": "Maria Silva"}, itens_count=1,
        subtotal="10.00", valor_frete="5.00", valor_total="15.00")
    value.update(extra)
    return value


def detail(**extra):
    value = dict(
        id=1, codigo="PED-1", data_pedido=1704067200000, status="PAGAMENTO_CONFIRMADO",
        cliente={"id": 42, "nome_completo": "Maria Silva", "email_masked": "mar*****"},
        entrega={"cep": "01001000", "logradouro": "Rua A", "numero": "10",
                 "complemento": "Ap 2", "bairro": "Centro", "cidade": "São Paulo",
                 "estado": "SP", "identificacao": "Casa"},
        itens=[item()], subtotal="10.00", valor_frete="5.00", valor_total="15.00",
        pagamento={"metodo": "PIX", "valor": "15.00", "status": "APROVADO"})
    value.update(extra)
    return value


def page_payload(**extra):
    value = dict(items=[summary()], page=1, per_page=20, items_total=1, page_total=1)
    value.update(extra)
    return value


def status_payload(**extra):
    value = dict(pedido_id=1, codigo="PED-1", status_anterior="PAGAMENTO_CONFIRMADO",
                 status_atual="EM_PREPARACAO", alterado=True)
    value.update(extra)
    return value


class OrderContractTests(unittest.TestCase):
    def test_filters_defaults_and_normalization(self):
        self.assertEqual(order_filters("  ", "TODOS", 1),
                         {"q": "", "status": "TODOS", "page": 1, "per_page": 20})
        self.assertEqual(order_filters(" PED-1 ", "ENVIADO", 2, 50),
                         {"q": "PED-1", "status": "ENVIADO", "page": 2, "per_page": 50})

    def test_filters_reject_invalid_values(self):
        for q, status, page, size in [
                (None, "TODOS", 1, 20), ("x" * 101, "TODOS", 1, 20),
                ("", "PAGO", 1, 20), ("", "TODOS", 0, 20),
                ("", "TODOS", True, 20), ("", "TODOS", 1, 51),
                ("", "TODOS", "1", 20)]:
            with self.assertRaises(ValueError):
                order_filters(q, status, page, size)

    def test_summary_preserves_values_and_display_fields(self):
        parsed = order_summary_record(summary())
        self.assertEqual((parsed.id, parsed.codigo, parsed.status), (1, "PED-1", "PAGAMENTO_CONFIRMADO"))
        self.assertEqual(parsed.data_pedido_display, "01/01/2024 às 00:00 (UTC)")
        self.assertEqual((parsed.cliente_id, parsed.cliente_nome, parsed.cliente_display),
                         (42, "Maria Silva", "Maria Silva"))
        self.assertEqual((parsed.itens_count, parsed.itens_count_display), (1, "1 item"))
        self.assertEqual((parsed.subtotal, parsed.valor_frete, parsed.valor_total),
                         ("10.00", "5.00", "15.00"))
        self.assertEqual(order_summary_record(summary(itens_count=0)).itens_count_display,
                         "0 itens")

    def test_summary_rejects_unexpected_or_invalid_fields(self):
        for value in [summary(extra=1), summary(status="PAGO"), summary(itens_count=-1),
                      summary(itens_count=True), summary(id=0), summary(codigo=""),
                      summary(cliente={"id": 42}),
                      summary(cliente={"id": 42, "nome_completo": "Maria", "email_masked": "m*****"}),
                      summary(valor_total="15,00"), summary(data_pedido=None)]:
            with self.assertRaises(ValueError):
                order_summary_record(value)

    def test_page_contract_and_empty_page(self):
        items, total, pages = order_summary_page(page_payload(), page=1)
        self.assertEqual((len(items), total, pages), (1, 1, 1))
        empty = page_payload(items=[], page=2, items_total=0, page_total=0)
        self.assertEqual(order_summary_page(empty, page=2)[1:], (0, 0))
        for value in [page_payload(page=2), page_payload(page_total=2),
                      page_payload(extra=1),
                      page_payload(items=[summary()], items_total=2, page_total=1),
                      page_payload(items=[summary(), summary()]),
                      page_payload(items=[summary(id=1), summary(id=1)], items_total=2),
                      page_payload(items_total=True)]:
            with self.assertRaises(ValueError):
                order_summary_page(value, page=1)

    def test_detail_preserves_values_and_display_fields(self):
        parsed = order_detail(detail(), order_id=1)
        self.assertEqual((parsed.id, parsed.codigo, parsed.status),
                         (1, "PED-1", "PAGAMENTO_CONFIRMADO"))
        self.assertEqual((parsed.cliente_id, parsed.cliente_nome, parsed.cliente_email_masked),
                         (42, "Maria Silva", "mar*****"))
        self.assertEqual(parsed.endereco_linha, "Rua A, 10, Ap 2")
        self.assertEqual(parsed.endereco_cidade, "Centro, São Paulo - SP")
        self.assertEqual(parsed.cep_display, "CEP 01001000")
        self.assertEqual(parsed.identificacao_display, "Casa")
        self.assertEqual(len(parsed.itens), 1)
        self.assertEqual((parsed.pagamento_metodo, parsed.pagamento_valor,
                          parsed.pagamento_status), ("PIX", "15.00", "APROVADO"))
        self.assertEqual((parsed.pagamento_metodo_display, parsed.pagamento_status_display),
                         ("PIX", "APROVADO"))

    def test_detail_normalizes_nulls_to_unavailable(self):
        parsed = order_detail(detail(
            cliente={"id": 42, "nome_completo": "Maria Silva", "email_masked": None},
            entrega={"cep": None, "logradouro": None, "numero": None,
                     "complemento": None, "bairro": None, "cidade": None,
                     "estado": None, "identificacao": None},
            pagamento={"metodo": None, "valor": "0.00", "status": None}), order_id=1)
        self.assertEqual(parsed.cliente_email_masked, "")
        self.assertEqual(parsed.endereco_linha, "Indisponível")
        self.assertEqual(parsed.endereco_cidade, "Indisponível")
        self.assertEqual(parsed.cep_display, "Indisponível")
        self.assertEqual(parsed.identificacao_display, "Indisponível")
        self.assertEqual((parsed.pagamento_metodo_display, parsed.pagamento_status_display),
                         ("Indisponível", "Indisponível"))

    def test_detail_rejects_unexpected_or_invalid_fields(self):
        unsafe_email = "maria@example.com"
        for value in [detail(extra=1), detail(status="PAGO"), detail(id=2),
                      detail(entrega={"cep": "1"}), detail(pagamento={"metodo": "PIX"}),
                      detail(cliente={"id": 42, "nome_completo": "Maria"}),
                      detail(cliente={"id": 42, "nome_completo": "Maria",
                                      "email_masked": unsafe_email}),
                      detail(itens={}), detail(itens=[item(extra=1)])]:
            with self.assertRaises(ValueError):
                order_detail(value, order_id=1)

    def test_status_result_contract(self):
        parsed = order_status_result(status_payload(), order_id=1)
        self.assertEqual((parsed.pedido_id, parsed.codigo, parsed.status_anterior,
                          parsed.status_atual, parsed.alterado),
                         (1, "PED-1", "PAGAMENTO_CONFIRMADO", "EM_PREPARACAO", True))
        for value in [status_payload(extra=1), status_payload(pedido_id=0),
                      status_payload(pedido_id=2), status_payload(status_anterior="PAGO"),
                      status_payload(status_atual="PAGO"), status_payload(alterado="yes"),
                      status_payload(codigo="")]:
            with self.assertRaises(ValueError):
                order_status_result(value, order_id=1)


class OrderWorkflowTests(unittest.IsolatedAsyncioTestCase):
    def state(self, role="FUNCIONARIO", user_id=9):
        state = SimpleNamespace(
            _auth_token="internal-fixture", is_authenticated=True,
            session_status="success", user_status="ATIVO", user_role=role,
            user_id=user_id,
            internal_orders=[], internal_order_detail=[],
            internal_orders_query="", internal_orders_status="TODOS",
            internal_orders_query_input="", internal_orders_status_input="TODOS",
            internal_orders_page=1, internal_orders_total=0, internal_orders_pages=0,
            internal_orders_loading=False, internal_order_loading=False,
            internal_orders_message="", internal_order_feedback="",
            internal_order_feedback_error=False, internal_order_saving=False,
            _internal_orders_generation=0, _internal_order_detail_generation=0)
        for method in ["_internal_customer_allowed", "_internal_order_allowed",
                       "_clear_internal_orders", "_clear_internal_order_detail",
                       "_reset_internal_order_filters", "_order_feedback"]:
            setattr(state, method, MethodType(getattr(app.State, method), state))

        def clear(message):
            state._clear_internal_orders()
            state._auth_token = ""
            state.is_authenticated = False
        state._clear_authentication_state = clear
        return state

    async def test_both_roles_use_internal_token_only(self):
        for role in ["FUNCIONARIO", "ADMINISTRADOR"]:
            state = self.state(role)
            with patch.object(app, "_required_environment_url",
                              return_value="https://example.test/pedidos"), \
                    patch.object(app, "_server_side_xano_request",
                                 AsyncMock(return_value=page_payload())) as request:
                await app.State.load_internal_orders.fn(state)
            self.assertEqual(state.internal_orders_total, 1)
            self.assertIn("status=TODOS", request.await_args.args[0])
            self.assertIn("per_page=20", request.await_args.args[0])
            self.assertEqual(request.await_args.kwargs["authorization"],
                             "Bearer internal-fixture")
            self.assertFalse(request.await_args.kwargs["retry_rate_limit"])

    async def test_customer_and_inactive_sessions_never_request(self):
        for role, status in [("CLIENTE", "ATIVO"), ("FUNCIONARIO", "INATIVO")]:
            state = self.state(role)
            state.user_status = status
            with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
                await app.State.load_internal_orders.fn(state)
            request.assert_not_awaited()

    async def test_logout_during_read_discards_result(self):
        state = self.state()

        async def request(*args, **kwargs):
            state._clear_authentication_state("logout")
            return page_payload()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/pedidos"), \
                patch.object(app, "_server_side_xano_request", side_effect=request):
            await app.State.load_internal_orders.fn(state)
        self.assertEqual(state.internal_orders, [])

    async def test_unauthorized_clears_data(self):
        for code in [401, 403]:
            state = self.state()
            state.internal_order_detail = [order_detail(detail(), order_id=1)]
            error = urllib.error.HTTPError("https://example.test", code, "denied", {}, io.BytesIO())
            with patch.object(app, "_required_environment_url",
                              return_value="https://example.test/pedidos"), \
                    patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
                await app.State.load_internal_orders.fn(state)
            self.assertFalse(state.is_authenticated)
            self.assertEqual(state.internal_order_detail, [])

    async def test_invalid_filters_never_request(self):
        state = self.state()
        state.internal_orders_status = "PAGO"
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.load_internal_orders.fn(state)
        request.assert_not_awaited()
        self.assertIn("Filtros inválidos", state.internal_orders_message)

    async def test_select_detail_populates(self):
        state = self.state()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/pedidos/{order_id}"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=detail())) as request:
            await app.State.select_internal_order.fn(state, 1)
        self.assertEqual(state.internal_order_detail[0].id, 1)
        self.assertIn("/pedidos/1", request.await_args.args[0])

    async def test_select_wrong_id_is_rejected(self):
        state = self.state()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/pedidos/{order_id}"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=detail(id=2))):
            await app.State.select_internal_order.fn(state, 1)
        self.assertEqual(state.internal_order_detail, [])
        self.assertTrue(state.internal_order_feedback_error)

    async def test_select_invalid_id_never_request(self):
        state = self.state()
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.select_internal_order.fn(state, "1")
        request.assert_not_awaited()

    async def test_select_stale_after_list_reload_is_discarded(self):
        state = self.state()

        async def request(*args, **kwargs):
            state._internal_orders_generation += 1
            return detail()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/pedidos/{order_id}"), \
                patch.object(app, "_server_side_xano_request", side_effect=request):
            await app.State.select_internal_order.fn(state, 1)
        self.assertEqual(state.internal_order_detail, [])

    async def test_select_notfound_shows_message(self):
        state = self.state()
        error = urllib.error.HTTPError("https://example.test", 404, "notfound", {}, io.BytesIO())
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/pedidos/{order_id}"), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.select_internal_order.fn(state, 1)
        self.assertEqual(state.internal_order_detail, [])
        self.assertIn("não encontrado", state.internal_order_feedback)

    async def test_employee_cannot_advance_status(self):
        state = self.state("FUNCIONARIO", user_id=9)
        state.internal_order_detail = [order_detail(detail(), order_id=1)]
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.advance_internal_order_status.fn(state)
        request.assert_not_awaited()
        self.assertTrue(state.internal_order_feedback_error)
        self.assertIn("administrador", state.internal_order_feedback)

    async def test_administrator_advances_one_step(self):
        state = self.state("ADMINISTRADOR", user_id=1)
        state.internal_order_detail = [order_detail(detail(), order_id=1)]
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/pedidos/{order_id}/status"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=status_payload())) as request:
            await app.State.advance_internal_order_status.fn(state)
        self.assertEqual(request.await_args.args[0], "https://example.test/pedidos/1/status")
        self.assertEqual(request.await_args.kwargs["method"], "POST")
        self.assertEqual(request.await_args.kwargs["payload"], {"status": "EM_PREPARACAO"})
        self.assertEqual(state.internal_order_detail[0].status, "EM_PREPARACAO")
        self.assertFalse(state.internal_order_feedback_error)

    async def test_advance_idempotent_message(self):
        state = self.state("ADMINISTRADOR", user_id=1)
        state.internal_order_detail = [order_detail(detail(), order_id=1)]
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/pedidos/{order_id}/status"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=status_payload(alterado=False))):
            await app.State.advance_internal_order_status.fn(state)
        self.assertIn("já estava", state.internal_order_feedback)

    async def test_terminal_status_has_no_next_step(self):
        for status in ["ENTREGUE", "CANCELADO", "AGUARDANDO_PAGAMENTO"]:
            state = self.state("ADMINISTRADOR", user_id=1)
            state.internal_order_detail = [order_detail(
                detail(status=status), order_id=1)]
            with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
                await app.State.advance_internal_order_status.fn(state)
            request.assert_not_awaited()
            self.assertTrue(state.internal_order_feedback_error)

    async def test_advance_accessdenied_keeps_session(self):
        state = self.state("ADMINISTRADOR", user_id=1)
        state.internal_order_detail = [order_detail(detail(), order_id=1)]
        error = urllib.error.HTTPError("https://example.test", 403, "forbidden", {}, io.BytesIO())
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/pedidos/{order_id}/status"), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.advance_internal_order_status.fn(state)
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.internal_order_detail[0].status, "PAGAMENTO_CONFIRMADO")
        self.assertTrue(state.internal_order_feedback_error)

    async def test_advance_invalid_transition_keeps_session(self):
        for code in [400, 404]:
            state = self.state("ADMINISTRADOR", user_id=1)
            state.internal_order_detail = [order_detail(detail(), order_id=1)]
            error = urllib.error.HTTPError("https://example.test", code, "bad", {}, io.BytesIO())
            with patch.object(app, "_required_environment_url",
                              return_value="https://example.test/pedidos/{order_id}/status"), \
                    patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
                await app.State.advance_internal_order_status.fn(state)
            self.assertTrue(state.is_authenticated)
            self.assertTrue(state.internal_order_feedback_error)

    async def test_advance_unauthorized_clears_session(self):
        state = self.state("ADMINISTRADOR", user_id=1)
        state.internal_order_detail = [order_detail(detail(), order_id=1)]
        error = urllib.error.HTTPError("https://example.test", 401, "denied", {}, io.BytesIO())
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/pedidos/{order_id}/status"), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.advance_internal_order_status.fn(state)
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.internal_order_detail, [])

    def test_apply_filters_resets_page_and_commits_values(self):
        state = self.state()
        state.internal_orders_page = 3
        app.State.apply_internal_order_filters.fn(state, {
            "q": "  PED-1 ", "status": "ENVIADO"})
        self.assertEqual((state.internal_orders_query, state.internal_orders_status,
                          state.internal_orders_query_input, state.internal_orders_status_input,
                          state.internal_orders_page),
                         ("PED-1", "ENVIADO", "PED-1", "ENVIADO", 1))

    def test_invalid_filters_keep_values(self):
        state = self.state()
        state.internal_orders_status = "ENVIADO"
        state.internal_orders_page = 2
        app.State.apply_internal_order_filters.fn(state, {
            "q": "", "status": "PAGO"})
        self.assertEqual(state.internal_orders_status, "ENVIADO")
        self.assertEqual(state.internal_orders_page, 2)
        self.assertIn("Filtros inválidos", state.internal_orders_message)

    def test_clear_filters_restores_defaults(self):
        state = self.state()
        state.internal_orders_query = "PED-1"
        state.internal_orders_status = "ENVIADO"
        state.internal_orders_page = 2
        app.State.clear_internal_order_filters.fn(state)
        self.assertEqual((state.internal_orders_query, state.internal_orders_status,
                          state.internal_orders_page), ("", "TODOS", 1))

    def test_pagination_is_bounded(self):
        state = self.state()
        state.internal_orders_pages = 2
        app.State.internal_orders_next.fn(state)
        self.assertEqual(state.internal_orders_page, 2)
        app.State.internal_orders_next.fn(state)
        self.assertEqual(state.internal_orders_page, 2)
        app.State.internal_orders_previous.fn(state)
        self.assertEqual(state.internal_orders_page, 1)
        state.internal_orders_loading = True
        app.State.internal_orders_next.fn(state)
        self.assertEqual(state.internal_orders_page, 1)

    def test_close_clears_detail(self):
        state = self.state()
        state.internal_order_detail = [order_detail(detail(), order_id=1)]
        app.State.close_internal_order.fn(state)
        self.assertEqual(state.internal_order_detail, [])
        self.assertEqual(state.internal_order_feedback, "")
