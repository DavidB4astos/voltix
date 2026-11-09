import io
import unittest
import urllib.error
from types import MethodType, SimpleNamespace
from unittest.mock import AsyncMock, patch

from voltix.internal_attendances import (attendance_filters, attendance_page,
    attendance_record, datetime_local_value, status_result)
import voltix.voltix as app


def record(**extra):
    value = dict(
        id=1, cliente_id=42, usuario_interno_id=9, pedido_id=None,
        assunto="Dúvida sobre pedido", descricao="Cliente relatou um problema.",
        status="ABERTO", data_atendimento=1704067200000,
        created_at=1704067200000, updated_at=1704067200000)
    value.update(extra)
    return value


def page_payload(**extra):
    value = dict(items=[record()], page=1, per_page=20, total_items=1, total_pages=1)
    value.update(extra)
    return value


def status_payload(**extra):
    value = dict(atendimento_id=1, status_anterior="ABERTO",
                 status_atual="EM_ATENDIMENTO", alterado=True)
    value.update(extra)
    return value


class AttendanceContractTests(unittest.TestCase):
    def test_filters_defaults_and_normalization(self):
        self.assertEqual(attendance_filters(None, "TODOS", 1),
                         {"status": "TODOS", "page": 1, "per_page": 20})
        self.assertEqual(attendance_filters(42, "EM_ATENDIMENTO", 2, 50),
                         {"status": "EM_ATENDIMENTO", "page": 2, "per_page": 50,
                          "cliente_id": 42})

    def test_filters_reject_invalid_values(self):
        for cliente, status, page, size in [
                (0, "TODOS", 1, 20), (True, "TODOS", 1, 20), ("1", "TODOS", 1, 20),
                (None, "PAGO", 1, 20), (None, "TODOS", 0, 20),
                (None, "TODOS", True, 20), (None, "TODOS", 1, 51)]:
            with self.assertRaises(ValueError):
                attendance_filters(cliente, status, page, size)

    def test_record_preserves_values_and_display_fields(self):
        parsed = attendance_record(record())
        self.assertEqual((parsed.id, parsed.cliente_id, parsed.usuario_interno_id),
                         (1, 42, 9))
        self.assertIsNone(parsed.pedido_id)
        self.assertEqual(parsed.cliente_display, "Cliente #42")
        self.assertEqual(parsed.pedido_display, "Sem pedido")
        self.assertEqual(parsed.responsavel_display, "Responsável #9")
        self.assertEqual(parsed.data_atendimento_display, "01/01/2024 às 00:00 (UTC)")
        self.assertEqual(parsed.data_atendimento_input, "2024-01-01T00:00")
        self.assertEqual(attendance_record(record(pedido_id=7)).pedido_display, "Pedido #7")

    def test_dates_accept_iso_and_handle_invalid_values(self):
        parsed = attendance_record(record(data_atendimento="2023-12-31T21:00:00-03:00"))
        self.assertEqual(parsed.data_atendimento_display, "01/01/2024 às 00:00 (UTC)")
        invalid = attendance_record(record(data_atendimento="invalid"))
        self.assertEqual(invalid.data_atendimento_display, "Data indisponível")
        self.assertEqual(invalid.data_atendimento_input, "")
        missing = attendance_record(record(data_atendimento=None))
        self.assertEqual(missing.data_atendimento_display, "Data indisponível")
        self.assertEqual(datetime_local_value(1704067200000), "2024-01-01T00:00")
        self.assertEqual(datetime_local_value("invalid"), "")

    def test_record_rejects_unexpected_or_invalid_fields(self):
        for value in [record(extra=1), record(status="PAGO"), record(pedido_id=0),
                      record(pedido_id=True), record(assunto=""), record(assunto="x" * 201),
                      record(descricao=""), record(descricao="x" * 2001),
                      record(id=True), record(cliente_id=0),
                      record(usuario_interno_id="9")]:
            with self.assertRaises(ValueError):
                attendance_record(value)

    def test_page_contract_and_empty_page(self):
        items, total, pages = attendance_page(page_payload(), page=1)
        self.assertEqual((len(items), total, pages), (1, 1, 1))
        empty = page_payload(items=[], page=2, total_items=0, total_pages=0)
        self.assertEqual(attendance_page(empty, page=2)[1:], (0, 0))
        for value in [page_payload(page=2), page_payload(total_pages=2),
                      page_payload(extra=1),
                      page_payload(items=[record()], total_items=2, total_pages=1),
                      page_payload(items=[record(), record()])]:
            with self.assertRaises(ValueError):
                attendance_page(value, page=1)

    def test_status_result_contract(self):
        parsed = status_result(status_payload())
        self.assertEqual((parsed.atendimento_id, parsed.status_anterior,
                          parsed.status_atual, parsed.alterado),
                         (1, "ABERTO", "EM_ATENDIMENTO", True))
        for value in [status_payload(extra=1), status_payload(atendimento_id=0),
                      status_payload(status_anterior="PAGO"),
                      status_payload(status_atual="PAGO"),
                      status_payload(alterado="yes")]:
            with self.assertRaises(ValueError):
                status_result(value)


class AttendanceWorkflowTests(unittest.IsolatedAsyncioTestCase):
    def state(self, role="FUNCIONARIO", user_id=9):
        state = SimpleNamespace(
            _auth_token="internal-fixture", is_authenticated=True,
            session_status="success", user_status="ATIVO", user_role=role,
            user_id=user_id,
            internal_attendances=[], internal_attendance_detail=[],
            internal_attendances_cliente_id="", internal_attendances_status="TODOS",
            internal_attendances_cliente_id_input="", internal_attendances_status_input="TODOS",
            internal_attendances_page=1, internal_attendances_total=0,
            internal_attendances_pages=0, internal_attendances_loading=False,
            internal_attendance_loading=False, internal_attendances_message="",
            internal_attendance_feedback="", internal_attendance_feedback_error=False,
            internal_attendance_form_cliente_id="", internal_attendance_form_pedido_id="",
            internal_attendance_form_assunto="", internal_attendance_form_descricao="",
            internal_attendance_form_data_atendimento="",
            internal_attendance_edit_assunto="", internal_attendance_edit_descricao="",
            internal_attendance_edit_data_atendimento="", internal_attendance_saving=False,
            _internal_attendances_generation=0, _internal_attendance_detail_generation=0)
        for method in ["_internal_customer_allowed", "_internal_attendance_allowed",
                       "_clear_internal_attendances", "_clear_internal_attendance_detail",
                       "_reset_internal_attendance_filters", "_attendance_feedback"]:
            setattr(state, method, MethodType(getattr(app.State, method), state))

        def clear(message):
            state._clear_internal_attendances()
            state._auth_token = ""
            state.is_authenticated = False
        state._clear_authentication_state = clear
        return state

    async def test_both_roles_use_internal_token_only(self):
        for role in ["FUNCIONARIO", "ADMINISTRADOR"]:
            state = self.state(role)
            with patch.object(app, "_required_environment_url",
                              return_value="https://example.test/atendimentos"), \
                    patch.object(app, "_server_side_xano_request",
                                 AsyncMock(return_value=page_payload())) as request:
                await app.State.load_internal_attendances.fn(state)
            self.assertEqual(state.internal_attendances_total, 1)
            self.assertIn("status=TODOS", request.await_args.args[0])
            self.assertEqual(request.await_args.kwargs["authorization"],
                             "Bearer internal-fixture")
            self.assertFalse(request.await_args.kwargs["retry_rate_limit"])

    async def test_customer_and_inactive_sessions_never_request(self):
        for role, status in [("CLIENTE", "ATIVO"), ("FUNCIONARIO", "INATIVO")]:
            state = self.state(role)
            state.user_status = status
            with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
                await app.State.load_internal_attendances.fn(state)
            request.assert_not_awaited()

    async def test_logout_during_read_discards_result(self):
        state = self.state()

        async def request(*args, **kwargs):
            state._clear_authentication_state("logout")
            return page_payload()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos"), \
                patch.object(app, "_server_side_xano_request", side_effect=request):
            await app.State.load_internal_attendances.fn(state)
        self.assertEqual(state.internal_attendances, [])

    async def test_unauthorized_clears_data(self):
        state = self.state()
        state.internal_attendance_detail = [attendance_record(record())]
        error = urllib.error.HTTPError("https://example.test", 403, "forbidden", {}, io.BytesIO())
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos"), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.load_internal_attendances.fn(state)
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.internal_attendance_detail, [])

    async def test_invalid_filters_never_request(self):
        state = self.state()
        state.internal_attendances_status = "PAGO"
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.load_internal_attendances.fn(state)
        request.assert_not_awaited()
        self.assertIn("Filtros inválidos", state.internal_attendances_message)

    async def test_select_detail_populates_edit_fields(self):
        state = self.state()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos/{attendance_id}"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=record())):
            await app.State.select_internal_attendance.fn(state, 1)
        self.assertEqual(state.internal_attendance_detail[0].id, 1)
        self.assertEqual(state.internal_attendance_edit_assunto, "Dúvida sobre pedido")
        self.assertEqual(state.internal_attendance_edit_data_atendimento, "2024-01-01T00:00")

    async def test_select_wrong_id_is_rejected(self):
        state = self.state()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos/{attendance_id}"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=record(id=2))):
            await app.State.select_internal_attendance.fn(state, 1)
        self.assertEqual(state.internal_attendance_detail, [])

    async def test_select_notfound_shows_message(self):
        state = self.state()
        error = urllib.error.HTTPError("https://example.test", 404, "notfound", {}, io.BytesIO())
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos/{attendance_id}"), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.select_internal_attendance.fn(state, 1)
        self.assertEqual(state.internal_attendance_detail, [])
        self.assertIn("não encontrado", state.internal_attendance_feedback)

    async def test_create_sends_only_allowed_fields(self):
        state = self.state()
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=record(id=2))) as request:
            await app.State.create_internal_attendance.fn(state, {
                "cliente_id": "42", "pedido_id": "7", "assunto": "Assunto",
                "descricao": "Descrição", "data_atendimento": "2026-11-09T10:00"})
        payload = request.await_args.kwargs["payload"]
        self.assertEqual(payload, {"cliente_id": 42, "pedido_id": 7, "assunto": "Assunto",
                                   "descricao": "Descrição",
                                   "data_atendimento": "2026-11-09T10:00"})
        self.assertNotIn("usuario_interno_id", payload)
        self.assertNotIn("status", payload)
        self.assertEqual(state.internal_attendance_form_assunto, "")
        self.assertEqual(state.internal_attendance_detail[0].id, 2)
        self.assertIn("criado", state.internal_attendance_feedback)

    async def test_create_invalid_keeps_form_and_does_not_request(self):
        state = self.state()
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.create_internal_attendance.fn(state, {
                "cliente_id": "42", "assunto": "", "descricao": "Descrição"})
        request.assert_not_awaited()
        self.assertTrue(state.internal_attendance_feedback_error)

    async def test_closed_attendance_cannot_be_edited(self):
        state = self.state()
        state.internal_attendance_detail = [attendance_record(record(status="FINALIZADO"))]
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.save_internal_attendance.fn(state, {
                "assunto": "Novo", "descricao": "Nova descrição"})
        request.assert_not_awaited()
        self.assertIn("somente leitura", state.internal_attendance_feedback)

    async def test_edit_sends_only_editable_fields(self):
        state = self.state()
        state.internal_attendance_detail = [attendance_record(record())]
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos/{attendance_id}"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=record(assunto="Novo",
                                                          descricao="Nova descrição"))) as request:
            await app.State.save_internal_attendance.fn(state, {
                "assunto": "Novo", "descricao": "Nova descrição",
                "data_atendimento": "2026-11-09T10:00"})
        payload = request.await_args.kwargs["payload"]
        self.assertEqual(set(payload), {"assunto", "descricao", "data_atendimento"})
        self.assertEqual(state.internal_attendance_detail[0].assunto, "Novo")

    async def test_any_employee_starts_attendance(self):
        state = self.state("FUNCIONARIO", user_id=9)
        state.internal_attendance_detail = [attendance_record(
            record(usuario_interno_id=99, status="ABERTO"))]
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos/{attendance_id}/status"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=status_payload())):
            await app.State.change_internal_attendance_status.fn(state, "EM_ATENDIMENTO")
        self.assertEqual(state.internal_attendance_detail[0].status, "EM_ATENDIMENTO")

    async def test_non_responsible_employee_cannot_finish(self):
        state = self.state("FUNCIONARIO", user_id=9)
        state.internal_attendance_detail = [attendance_record(
            record(usuario_interno_id=99, status="EM_ATENDIMENTO"))]
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.change_internal_attendance_status.fn(state, "FINALIZADO")
        request.assert_not_awaited()
        self.assertTrue(state.internal_attendance_feedback_error)
        self.assertIn("responsável", state.internal_attendance_feedback)

    async def test_responsible_employee_finishes(self):
        state = self.state("FUNCIONARIO", user_id=9)
        state.internal_attendance_detail = [attendance_record(
            record(usuario_interno_id=9, status="ABERTO"))]
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos/{attendance_id}/status"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=status_payload(
                                 status_atual="FINALIZADO"))):
            await app.State.change_internal_attendance_status.fn(state, "FINALIZADO")
        self.assertEqual(state.internal_attendance_detail[0].status, "FINALIZADO")

    async def test_administrator_cancels_for_another_responsible(self):
        state = self.state("ADMINISTRADOR", user_id=1)
        state.internal_attendance_detail = [attendance_record(
            record(usuario_interno_id=99, status="EM_ATENDIMENTO"))]
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos/{attendance_id}/status"), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=status_payload(
                                 status_atual="CANCELADO"))):
            await app.State.change_internal_attendance_status.fn(state, "CANCELADO")
        self.assertEqual(state.internal_attendance_detail[0].status, "CANCELADO")

    async def test_same_status_is_idempotent_without_request(self):
        state = self.state()
        state.internal_attendance_detail = [attendance_record(record(status="ABERTO"))]
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.change_internal_attendance_status.fn(state, "ABERTO")
        request.assert_not_awaited()
        self.assertFalse(state.internal_attendance_feedback_error)

    async def test_closed_attendance_rejects_transition(self):
        state = self.state("ADMINISTRADOR", user_id=1)
        state.internal_attendance_detail = [attendance_record(record(status="FINALIZADO"))]
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.change_internal_attendance_status.fn(state, "EM_ATENDIMENTO")
        request.assert_not_awaited()
        self.assertTrue(state.internal_attendance_feedback_error)

    async def test_status_accessdenied_keeps_session(self):
        state = self.state()
        state.internal_attendance_detail = [attendance_record(
            record(usuario_interno_id=9, status="ABERTO"))]
        error = urllib.error.HTTPError("https://example.test", 403, "forbidden", {}, io.BytesIO())
        with patch.object(app, "_required_environment_url",
                          return_value="https://example.test/atendimentos/{attendance_id}/status"), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.change_internal_attendance_status.fn(state, "FINALIZADO")
        self.assertTrue(state.is_authenticated)
        self.assertTrue(state.internal_attendance_feedback_error)

    def test_apply_filters_resets_page_and_commits_values(self):
        state = self.state()
        state.internal_attendances_page = 3
        app.State.apply_internal_attendance_filters.fn(state, {
            "cliente_id": "42", "status": "EM_ATENDIMENTO"})
        self.assertEqual((state.internal_attendances_cliente_id,
                          state.internal_attendances_status,
                          state.internal_attendances_page),
                         ("42", "EM_ATENDIMENTO", 1))

    def test_invalid_filters_keep_values(self):
        state = self.state()
        state.internal_attendances_status = "ABERTO"
        state.internal_attendances_page = 2
        app.State.apply_internal_attendance_filters.fn(state, {
            "cliente_id": "0", "status": "ABERTO"})
        self.assertEqual(state.internal_attendances_status, "ABERTO")
        self.assertEqual(state.internal_attendances_page, 2)
        self.assertIn("Filtros inválidos", state.internal_attendances_message)

    def test_clear_filters_restores_defaults(self):
        state = self.state()
        state.internal_attendances_cliente_id = "42"
        state.internal_attendances_status = "ABERTO"
        state.internal_attendances_page = 2
        app.State.clear_internal_attendance_filters.fn(state)
        self.assertEqual((state.internal_attendances_cliente_id,
                          state.internal_attendances_status,
                          state.internal_attendances_page), ("", "TODOS", 1))

    def test_pagination_is_bounded(self):
        state = self.state()
        state.internal_attendances_pages = 2
        app.State.internal_attendances_next.fn(state)
        self.assertEqual(state.internal_attendances_page, 2)
        app.State.internal_attendances_next.fn(state)
        self.assertEqual(state.internal_attendances_page, 2)
        app.State.internal_attendances_previous.fn(state)
        self.assertEqual(state.internal_attendances_page, 1)
        state.internal_attendances_loading = True
        app.State.internal_attendances_next.fn(state)
        self.assertEqual(state.internal_attendances_page, 1)
