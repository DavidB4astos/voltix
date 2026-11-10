import io
import unittest
import urllib.error
from types import MethodType, SimpleNamespace
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

from voltix.internal_attendances import attendance_record
from voltix.internal_crm import CRM_STATUS_ORDER, crm_dashboard
from voltix.internal_sales import dashboard_filters, sales_dashboard
import voltix.voltix as app


CRM_URLS = {
    "XANO_INTERNAL_CUSTOMERS_URL": "https://example.test/customers",
    "XANO_INTERNAL_ATTENDANCES_URL": "https://example.test/attendances",
    "XANO_INTERNAL_ORDERS_URL": "https://example.test/orders",
    "XANO_INTERNAL_SALES_URL": "https://example.test/sales",
}

SALES_STATUSES = ["PAGAMENTO_CONFIRMADO", "EM_PREPARACAO", "ENVIADO", "ENTREGUE"]


def attendance_data(record_id=1, status="ABERTO"):
    return dict(
        id=record_id, cliente_id=42, usuario_interno_id=9, pedido_id=None,
        assunto="Dúvida sobre pedido", descricao="Cliente relatou um problema.",
        status=status, data_atendimento=1704067200000,
        created_at=1704067200000, updated_at=1704067200000)


def attendance(record_id=1, status="ABERTO"):
    return attendance_record(attendance_data(record_id, status))


def customer():
    return dict(id=42, nome_completo="Cliente Fictício", email_masked="abc*****",
                telefone_masked="*****1234", status="ATIVO",
                created_at=1704067200000)


def order():
    return dict(
        id=7, codigo="PED-7", data_pedido=1704067200000,
        status="AGUARDANDO_PAGAMENTO",
        cliente={"id": 42, "nome_completo": "Cliente Fictício"},
        itens_count=1, subtotal=10.0, valor_frete=0.0, valor_total=10.0)


def sales_payload():
    return dict(
        periodo={"inicio": "2026-10-01", "fim": "2026-10-30", "timezone": "UTC"},
        faturamento=1000.0, pedidos=2, ticket_medio=500.0,
        status_incluidos=list(SALES_STATUSES),
        serie_diaria=[
            {"data": "2026-10-01", "faturamento": 400.0, "pedidos": 1},
            {"data": "2026-10-30", "faturamento": 600.0, "pedidos": 1},
        ])


def response_for(url):
    parsed = urlparse(url)
    parameters = parse_qs(parsed.query)
    if parsed.path == "/customers":
        return {"items": [customer()], "page": 1, "per_page": 1,
                "total_items": 5, "total_pages": 5}
    if parsed.path == "/attendances":
        per_page = int(parameters["per_page"][0])
        status = parameters["status"][0]
        if per_page == 10:
            items = [attendance_data(1, "FINALIZADO"), attendance_data(2, "ABERTO")]
            return {"items": items, "page": 1, "per_page": 10,
                    "total_items": 2, "total_pages": 1}
        totals = {"ABERTO": 3, "EM_ATENDIMENTO": 2, "FINALIZADO": 1}
        return {"items": [attendance_data(10, status)], "page": 1, "per_page": 1,
                "total_items": totals[status], "total_pages": totals[status]}
    if parsed.path == "/orders":
        return {"items": [order()], "page": 1, "per_page": 1,
                "items_total": 4, "page_total": 4}
    if parsed.path == "/sales":
        return sales_payload()
    raise AssertionError(f"Unexpected URL: {url}")


class CrmContractTests(unittest.TestCase):
    def snapshot(self, **extra):
        arguments = dict(
            clientes_ativos=5,
            atendimentos_por_status={"ABERTO": 3, "EM_ATENDIMENTO": 2, "FINALIZADO": 1},
            atendimentos_total=6,
            pedidos_total=4,
            recentes=[attendance(1), attendance(2, "FINALIZADO")],
            vendas=sales_dashboard(sales_payload()),
        )
        arguments.update(extra)
        return crm_dashboard(**arguments)

    def test_snapshot_preserves_counts_and_sales_values(self):
        snapshot = self.snapshot()
        self.assertEqual(snapshot.clientes_ativos, 5)
        self.assertEqual(snapshot.atendimentos_abertos, 3)
        self.assertEqual(snapshot.atendimentos_em_atendimento, 2)
        self.assertEqual(snapshot.atendimentos_finalizados, 1)
        self.assertEqual(snapshot.atendimentos_total, 6)
        self.assertEqual(snapshot.pedidos_total, 4)
        self.assertEqual(len(snapshot.recentes), 2)
        self.assertEqual(snapshot.faturamento, "1000.00")
        self.assertEqual(snapshot.vendas_pedidos, 2)
        self.assertEqual(snapshot.ticket_medio, "500.00")
        self.assertEqual(snapshot.vendas_periodo_display,
                         "01/10/2026 a 30/10/2026 (UTC)")

    def test_snapshot_accepts_empty_collections(self):
        snapshot = self.snapshot(
            clientes_ativos=0,
            atendimentos_por_status={status: 0 for status in CRM_STATUS_ORDER},
            atendimentos_total=0, pedidos_total=0, recentes=[])
        self.assertEqual((snapshot.clientes_ativos, snapshot.atendimentos_total),
                         (0, 0))
        self.assertEqual(snapshot.recentes, [])

    def test_snapshot_rejects_invalid_counts(self):
        for extra in [
                {"clientes_ativos": -1}, {"clientes_ativos": True},
                {"clientes_ativos": 1.0}, {"clientes_ativos": "5"},
                {"atendimentos_total": -1}, {"pedidos_total": True},
                {"atendimentos_por_status": {"ABERTO": 3, "EM_ATENDIMENTO": 2}},
                {"atendimentos_por_status": {
                    "ABERTO": 3, "EM_ATENDIMENTO": 2, "FINALIZADO": 1,
                    "CANCELADO": 0}},
                {"atendimentos_por_status": {
                    "ABERTO": -1, "EM_ATENDIMENTO": 2, "FINALIZADO": 1}},
                {"atendimentos_por_status": "TODOS"}]:
            with self.assertRaises(ValueError):
                self.snapshot(**extra)

    def test_snapshot_rejects_invalid_recent_attendances(self):
        valid = attendance(1)
        for extra in [
                {"recentes": "ABERTO"},
                {"recentes": [valid] * 11},
                {"recentes": [valid, valid]},
                {"recentes": [object()]},
                {"atendimentos_total": 1,
                 "recentes": [attendance(1), attendance(2)]}]:
            with self.assertRaises(ValueError):
                self.snapshot(**extra)

    def test_snapshot_rejects_invalid_sales(self):
        for value in [None, sales_payload(), object()]:
            with self.assertRaises(ValueError):
                self.snapshot(vendas=value)

    def test_sales_contract_is_reused(self):
        self.assertEqual(dashboard_filters(None, None), {})


class CrmHandlerTests(unittest.IsolatedAsyncioTestCase):
    def state(self, role="FUNCIONARIO", user_id=9):
        state = SimpleNamespace(
            _auth_token="internal-fixture", is_authenticated=True,
            session_status="success", user_status="ATIVO", user_role=role,
            user_id=user_id,
            internal_crm=[], internal_crm_loading=False,
            internal_crm_message="", internal_crm_loaded=False,
            _internal_crm_generation=0, internal_section="clientes")
        for method in ["_internal_customer_allowed", "_internal_crm_allowed",
                       "_clear_internal_crm"]:
            setattr(state, method, MethodType(getattr(app.State, method), state))

        def clear(message):
            state._clear_internal_crm()
            state._auth_token = ""
            state.is_authenticated = False
            state.session_status = "error"
            state.session_message = message
        state._clear_authentication_state = clear
        return state

    async def run_handler(self, state, request):
        with patch.object(app, "_required_environment_url",
                          side_effect=lambda name: CRM_URLS[name]), \
                patch.object(app, "_server_side_xano_request", request):
            await app.State.load_internal_crm.fn(state)

    async def test_snapshot_is_loaded_from_published_endpoints(self):
        request = AsyncMock(side_effect=lambda url, **kwargs: response_for(url))
        state = self.state()
        await self.run_handler(state, request)
        self.assertEqual(state.internal_crm_message, "")
        snapshot = state.internal_crm[0]
        self.assertEqual(snapshot.clientes_ativos, 5)
        self.assertEqual(snapshot.atendimentos_abertos, 3)
        self.assertEqual(snapshot.atendimentos_em_atendimento, 2)
        self.assertEqual(snapshot.atendimentos_finalizados, 1)
        self.assertEqual(snapshot.pedidos_total, 4)
        self.assertEqual(len(snapshot.recentes), 2)
        self.assertTrue(state.internal_crm_loaded)
        self.assertFalse(state.internal_crm_loading)
        self.assertEqual(request.await_count, 7)
        for call in request.await_args_list:
            self.assertEqual(call.kwargs["authorization"], "Bearer internal-fixture")
            self.assertFalse(call.kwargs["retry_rate_limit"])

    async def test_totals_use_one_item_pages_and_recent_uses_ten(self):
        request = AsyncMock(side_effect=lambda url, **kwargs: response_for(url))
        state = self.state()
        await self.run_handler(state, request)
        queries = [parse_qs(urlparse(call.args[0]).query)
                   for call in request.await_args_list]
        attendance_queries = [
            query for call, query in zip(request.await_args_list, queries)
            if urlparse(call.args[0]).path == "/attendances"]
        self.assertEqual([query["per_page"][0] for query in attendance_queries],
                         ["1", "1", "1", "10"])
        self.assertEqual([query["status"][0] for query in attendance_queries],
                         ["ABERTO", "EM_ATENDIMENTO", "FINALIZADO", "TODOS"])
        self.assertEqual(parse_qs(urlparse(request.await_args_list[0].args[0]).query),
                         {"status": ["ATIVO"], "page": ["1"], "per_page": ["1"]})
        self.assertEqual(parse_qs(urlparse(request.await_args_list[4].args[0]).query,
                                  keep_blank_values=True),
                         {"q": [""], "status": ["TODOS"], "page": ["1"],
                          "per_page": ["1"]})
        self.assertEqual(request.await_args_list[6].args[0], "https://example.test/sales")

    async def test_both_roles_load_and_customer_or_inactive_never_request(self):
        for role in ["FUNCIONARIO", "ADMINISTRADOR"]:
            state = self.state(role)
            await self.run_handler(
                state, AsyncMock(side_effect=lambda url, **kwargs: response_for(url)))
            self.assertEqual(len(state.internal_crm), 1)
        for role, status in [("CLIENTE", "ATIVO"), ("FUNCIONARIO", "INATIVO")]:
            state = self.state(role)
            state.user_status = status
            request = AsyncMock()
            await self.run_handler(state, request)
            request.assert_not_awaited()
            self.assertEqual(state.internal_crm, [])

    async def test_partial_failure_shows_no_numbers(self):
        async def request(url, **kwargs):
            if urlparse(url).path == "/orders":
                raise urllib.error.URLError("offline")
            return response_for(url)
        state = self.state()
        await self.run_handler(state, request)
        self.assertEqual(state.internal_crm, [])
        self.assertFalse(state.internal_crm_loaded)
        self.assertIn("Não foi possível carregar o CRM", state.internal_crm_message)
        self.assertFalse(state.internal_crm_loading)

    async def test_unauthorized_read_ends_the_session(self):
        async def request(url, **kwargs):
            raise urllib.error.HTTPError(url, 401, "unauthorized", {}, io.BytesIO(b""))
        state = self.state("ADMINISTRADOR")
        await self.run_handler(state, request)
        self.assertEqual(state.internal_crm, [])
        self.assertEqual(state._auth_token, "")
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.session_status, "error")
        self.assertIn("Acesso interno não autorizado", state.session_message)

    async def test_stale_response_is_discarded(self):
        async def request(url, **kwargs):
            state._auth_token = "other-token"
            return response_for(url)
        state = self.state()
        await self.run_handler(state, request)
        self.assertEqual(state.internal_crm, [])
        self.assertFalse(state.internal_crm_loading)


class CrmNavigationTests(unittest.TestCase):
    def state(self, role="FUNCIONARIO"):
        state = app.State(_reflex_internal_init=True)
        state._auth_token = "isolated-test-token"
        state.is_authenticated = True
        state.session_status = "success"
        state.user_status = "ATIVO"
        state.user_role = role
        return state

    def test_crm_is_available_to_both_internal_roles(self):
        for role in ["FUNCIONARIO", "ADMINISTRADOR"]:
            state = self.state(role)
            app.State.select_internal_section.fn(state, "crm")
            self.assertEqual(state.internal_section, "crm")

    def test_unknown_section_is_still_rejected(self):
        state = self.state()
        app.State.select_internal_section.fn(state, "crm")
        app.State.select_internal_section.fn(state, "unknown")
        self.assertEqual(state.internal_section, "crm")

    def test_logout_clears_crm_state(self):
        state = self.state("ADMINISTRADOR")
        state.internal_crm = [crm_dashboard(
            clientes_ativos=0,
            atendimentos_por_status={status: 0 for status in CRM_STATUS_ORDER},
            atendimentos_total=0, pedidos_total=0, recentes=[],
            vendas=sales_dashboard(sales_payload()))]
        state.internal_crm_loaded = True
        state._clear_authentication_state("logout", session_status="idle")
        self.assertEqual(state.internal_crm, [])
        self.assertFalse(state.internal_crm_loaded)
        self.assertEqual(state.internal_section, "clientes")


if __name__ == "__main__":
    unittest.main()
