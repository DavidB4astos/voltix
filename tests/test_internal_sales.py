import io
import unittest
import urllib.error
from types import MethodType, SimpleNamespace
from unittest.mock import AsyncMock, patch

from voltix.internal_sales import dashboard_filters, sales_dashboard
import voltix.voltix as app

STATUSES = ["PAGAMENTO_CONFIRMADO", "EM_PREPARACAO", "ENVIADO", "ENTREGUE"]


def dashboard_payload(**extra):
    value = dict(
        periodo={"inicio": "2026-10-01", "fim": "2026-10-31", "timezone": "UTC"},
        faturamento=1000.0,
        pedidos=2,
        ticket_medio=500.0,
        status_incluidos=list(STATUSES),
        serie_diaria=[
            {"data": "2026-10-01", "faturamento": 400.0, "pedidos": 1},
            {"data": "2026-10-31", "faturamento": 600.0, "pedidos": 1},
        ])
    value.update(extra)
    return value


def empty_payload(**extra):
    value = dict(
        periodo={"inicio": "2026-10-01", "fim": "2026-10-31", "timezone": "UTC"},
        faturamento=0, pedidos=0, ticket_medio=0,
        status_incluidos=list(STATUSES), serie_diaria=[])
    value.update(extra)
    return value


class SalesContractTests(unittest.TestCase):
    def test_filters_defaults_and_explicit_range(self):
        self.assertEqual(dashboard_filters(None, None), {})
        self.assertEqual(dashboard_filters("", "  "), {})
        self.assertEqual(dashboard_filters("2026-10-01", None), {"from": "2026-10-01"})
        self.assertEqual(dashboard_filters(None, "2026-10-31"), {"to": "2026-10-31"})
        self.assertEqual(dashboard_filters("2026-10-01", "2026-10-31"),
                         {"from": "2026-10-01", "to": "2026-10-31"})

    def test_filters_accept_maximum_inclusive_window(self):
        self.assertEqual(dashboard_filters("2025-01-01", "2025-12-31"),
                         {"from": "2025-01-01", "to": "2025-12-31"})

    def test_filters_reject_invalid_values(self):
        for start, end in [
                (42, None), (None, 42), ("2026-13-01", None), ("2026-02-30", None),
                ("01/10/2026", None), ("2026-10-31", "2026-10-01"),
                ("2025-01-01", "2026-01-02")]:
            with self.assertRaises(ValueError):
                dashboard_filters(start, end)

    def test_dashboard_preserves_values_and_display_fields(self):
        parsed = sales_dashboard(dashboard_payload())
        self.assertEqual((parsed.periodo_inicio, parsed.periodo_fim,
                          parsed.periodo_timezone),
                         ("2026-10-01", "2026-10-31", "UTC"))
        self.assertEqual(parsed.periodo_display, "01/10/2026 a 31/10/2026 (UTC)")
        self.assertEqual((parsed.faturamento, parsed.pedidos, parsed.ticket_medio),
                         ("1000.00", 2, "500.00"))
        self.assertEqual(parsed.status_incluidos_display,
                         "Pagamento confirmado, Em preparação, Enviado, Entregue")
        self.assertEqual(len(parsed.serie_diaria), 2)
        self.assertEqual(parsed.serie_diaria[0].data_display, "01/10/2026")
        self.assertEqual(parsed.serie_diaria[0].faturamento, "400.00")

    def test_money_values_are_canonical_two_decimals(self):
        parsed = sales_dashboard(dashboard_payload(
            faturamento=1000, ticket_medio=500,
            serie_diaria=[{"data": "2026-10-01", "faturamento": 400, "pedidos": 2}]))
        self.assertEqual(parsed.faturamento, "1000.00")
        self.assertEqual(parsed.ticket_medio, "500.00")
        self.assertEqual(parsed.serie_diaria[0].faturamento, "400.00")

    def test_empty_period_is_accepted(self):
        parsed = sales_dashboard(empty_payload())
        self.assertEqual((parsed.faturamento, parsed.pedidos, parsed.ticket_medio),
                         ("0.00", 0, "0.00"))
        self.assertEqual(parsed.serie_diaria, [])

    def test_dashboard_rejects_unexpected_or_invalid_fields(self):
        for value in [dashboard_payload(extra=1), dashboard_payload(timezone="UTC"),
                      dashboard_payload(periodo={"inicio": "2026-10-01"}),
                      dashboard_payload(periodo={"inicio": "2026-10-01",
                                                 "fim": "2026-10-31", "timezone": "UTC",
                                                 "extra": 1}),
                      dashboard_payload(periodo={"inicio": "2026-10-31",
                                                 "fim": "2026-10-01", "timezone": "UTC"}),
                      dashboard_payload(periodo={"inicio": "2026-10-01",
                                                 "fim": "2026-10-31", "timezone": "America/Sao_Paulo"}),
                      dashboard_payload(status_incluidos=list(reversed(STATUSES))),
                      dashboard_payload(status_incluidos=STATUSES[:3]),
                      dashboard_payload(status_incluidos="TODOS"),
                      dashboard_payload(pedidos=-1), dashboard_payload(pedidos=True),
                      dashboard_payload(pedidos=2.0), dashboard_payload(faturamento=-1),
                      dashboard_payload(faturamento="abc"), dashboard_payload(ticket_medio=-1)]:
            with self.assertRaises(ValueError):
                sales_dashboard(value)

    def test_dashboard_rejects_invalid_series(self):
        duplicate = [{"data": "2026-10-01", "faturamento": 400.0, "pedidos": 1},
                     {"data": "2026-10-01", "faturamento": 600.0, "pedidos": 1}]
        descending = [{"data": "2026-10-31", "faturamento": 400.0, "pedidos": 1},
                      {"data": "2026-10-01", "faturamento": 600.0, "pedidos": 1}]
        outside = [{"data": "2026-09-30", "faturamento": 1000.0, "pedidos": 2}]
        for value in [dashboard_payload(serie_diaria=duplicate),
                      dashboard_payload(serie_diaria=descending),
                      dashboard_payload(serie_diaria=outside),
                      dashboard_payload(serie_diaria=[{"data": "2026-10-01"}]),
                      dashboard_payload(serie_diaria=[{"data": "2026-10-01",
                                                       "faturamento": 1000.0, "pedidos": 0}]),
                      dashboard_payload(serie_diaria=[{"data": "2026-10-01",
                                                       "faturamento": 1000.0, "pedidos": 1}]),
                      dashboard_payload(serie_diaria=[]),
                      dashboard_payload(ticket_medio=100.0)]:
            with self.assertRaises(ValueError):
                sales_dashboard(value)

    def test_empty_dashboard_rejects_inconsistent_values(self):
        for value in [empty_payload(faturamento=10.0), empty_payload(ticket_medio=1.0),
                      empty_payload(serie_diaria=[{"data": "2026-10-01",
                                                   "faturamento": 10.0, "pedidos": 1}])]:
            with self.assertRaises(ValueError):
                sales_dashboard(value)


class SalesWorkflowTests(unittest.IsolatedAsyncioTestCase):
    def state(self, role="FUNCIONARIO", user_id=9):
        state = SimpleNamespace(
            _auth_token="internal-fixture", is_authenticated=True,
            session_status="success", user_status="ATIVO", user_role=role,
            user_id=user_id,
            internal_dashboard=[], internal_dashboard_from="",
            internal_dashboard_to="", internal_dashboard_from_input="",
            internal_dashboard_to_input="", internal_dashboard_loading=False,
            internal_dashboard_message="", _internal_dashboard_generation=0)
        for method in ["_internal_customer_allowed", "_internal_dashboard_allowed",
                       "_clear_internal_dashboard", "_reset_internal_dashboard_filters"]:
            setattr(state, method, MethodType(getattr(app.State, method), state))

        def clear(message):
            state._clear_internal_dashboard()
            state._auth_token = ""
            state.is_authenticated = False
        state._clear_authentication_state = clear
        return state

    async def test_both_roles_use_internal_token_only(self):
        for role in ["FUNCIONARIO", "ADMINISTRADOR"]:
            state = self.state(role)
            with patch.object(app, "_required_environment_url",
                              return_value="https://example.test/sales"), \
                    patch.object(app, "_server_side_xano_request",
                                 AsyncMock(return_value=dashboard_payload())) as request:
                await app.State.load_internal_dashboard.fn(state)
            self.assertEqual(state.internal_dashboard[0].pedidos, 2)
            self.assertEqual(request.await_args.args[0], "https://example.test/sales")
            self.assertEqual(request.await_args.kwargs["authorization"],
                             "Bearer internal-fixture")
            self.assertFalse(request.await_args.kwargs["retry_rate_limit"])

    async def test_applied_period_is_sent(self):
        state = self.state()
        state.internal_dashboard_from = "2026-10-01"
        state.internal_dashboard_to = "2026-10-31"
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/sales"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=dashboard_payload())) as request:
            await app.State.load_internal_dashboard.fn(state)
        url = request.await_args.args[0]
        self.assertIn("from=2026-10-01", url)
        self.assertIn("to=2026-10-31", url)

    async def test_customer_and_inactive_sessions_never_request(self):
        for role, status in [("CLIENTE", "ATIVO"), ("FUNCIONARIO", "INATIVO")]:
            state = self.state(role)
            state.user_status = status
            with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
                await app.State.load_internal_dashboard.fn(state)
            request.assert_not_awaited()

    async def test_logout_during_read_discards_result(self):
        state = self.state()

        async def request(*args, **kwargs):
            state._clear_authentication_state("logout")
            return dashboard_payload()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/sales"), \
                patch.object(app, "_server_side_xano_request", side_effect=request):
            await app.State.load_internal_dashboard.fn(state)
        self.assertEqual(state.internal_dashboard, [])

    async def test_stale_response_is_discarded(self):
        state = self.state()

        async def request(*args, **kwargs):
            state._internal_dashboard_generation += 1
            return dashboard_payload()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/sales"), \
                patch.object(app, "_server_side_xano_request", side_effect=request):
            await app.State.load_internal_dashboard.fn(state)
        self.assertEqual(state.internal_dashboard, [])

    async def test_unauthorized_clears_data(self):
        for code in [401, 403]:
            state = self.state()
            error = urllib.error.HTTPError("https://example.test", code, "denied", {}, io.BytesIO())
            with patch.object(app, "_required_environment_url",
                              return_value="https://example.test/sales"), \
                    patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
                await app.State.load_internal_dashboard.fn(state)
            self.assertFalse(state.is_authenticated)
            self.assertEqual(state.internal_dashboard, [])

    async def test_invalid_applied_filters_never_request(self):
        state = self.state()
        state.internal_dashboard_from = "2026-10-31"
        state.internal_dashboard_to = "2026-10-01"
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.load_internal_dashboard.fn(state)
        request.assert_not_awaited()
        self.assertIn("Período inválido", state.internal_dashboard_message)

    async def test_backend_bad_request_keeps_session(self):
        state = self.state()
        error = urllib.error.HTTPError("https://example.test", 400, "bad", {}, io.BytesIO())
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/sales"), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.load_internal_dashboard.fn(state)
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.internal_dashboard, [])
        self.assertIn("Período inválido", state.internal_dashboard_message)

    async def test_network_error_keeps_session(self):
        state = self.state()
        error = urllib.error.URLError("offline")
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/sales"), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.load_internal_dashboard.fn(state)
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.internal_dashboard, [])
        self.assertIn("Não foi possível carregar", state.internal_dashboard_message)

    async def test_malformed_payload_is_not_rendered(self):
        state = self.state()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/sales"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=dashboard_payload(extra=1))):
            await app.State.load_internal_dashboard.fn(state)
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.internal_dashboard, [])
        self.assertIn("Não foi possível carregar", state.internal_dashboard_message)

    async def test_empty_period_is_stored(self):
        state = self.state()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/sales"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=empty_payload())):
            await app.State.load_internal_dashboard.fn(state)
        self.assertEqual(state.internal_dashboard[0].pedidos, 0)
        self.assertIn("Nenhuma venda", state.internal_dashboard_message)

    def test_apply_filters_commits_period(self):
        state = self.state()
        app.State.apply_internal_dashboard_filters.fn(state, {
            "from": "2026-10-01", "to": "2026-10-31"})
        self.assertEqual((state.internal_dashboard_from, state.internal_dashboard_to,
                          state.internal_dashboard_from_input,
                          state.internal_dashboard_to_input),
                         ("2026-10-01", "2026-10-31", "2026-10-01", "2026-10-31"))

    def test_apply_default_filters_clears_period(self):
        state = self.state()
        state.internal_dashboard_from = "2026-10-01"
        state.internal_dashboard_to = "2026-10-31"
        app.State.apply_internal_dashboard_filters.fn(state, {"from": "", "to": ""})
        self.assertEqual((state.internal_dashboard_from, state.internal_dashboard_to),
                         ("", ""))

    def test_invalid_filters_keep_values(self):
        state = self.state()
        state.internal_dashboard_from = "2026-10-01"
        state.internal_dashboard_to = "2026-10-31"
        app.State.apply_internal_dashboard_filters.fn(state, {
            "from": "2026-10-31", "to": "2026-10-01"})
        self.assertEqual((state.internal_dashboard_from, state.internal_dashboard_to),
                         ("2026-10-01", "2026-10-31"))
        self.assertIn("Período inválido", state.internal_dashboard_message)

    def test_clear_filters_restores_defaults(self):
        state = self.state()
        state.internal_dashboard_from = "2026-10-01"
        state.internal_dashboard_to = "2026-10-31"
        state.internal_dashboard_from_input = "2026-10-01"
        state.internal_dashboard_to_input = "2026-10-31"
        app.State.clear_internal_dashboard_filters.fn(state)
        self.assertEqual((state.internal_dashboard_from, state.internal_dashboard_to,
                          state.internal_dashboard_from_input,
                          state.internal_dashboard_to_input), ("", "", "", ""))
