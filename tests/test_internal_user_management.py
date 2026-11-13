import io
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import AsyncMock, patch

import voltix.voltix as app
from voltix.internal_users import (
    internal_user_list,
    internal_user_record,
    password_change_payload,
    profile_update_payload,
    user_create_payload,
    user_status_payload,
    user_update_payload,
)

USERS_URL = "https://example.test/internal-users"
UPDATE_URL = "https://example.test/internal-users/{user_id}"
PROFILE_URL = "https://example.test/internal-users/profile"
PASSWORD_URL = "https://example.test/internal-users/profile/password"
ROOT = Path("xano/api/internal_users")


def urls(name):
    return {
        "XANO_INTERNAL_USERS_URL": USERS_URL,
        "XANO_INTERNAL_USER_UPDATE_URL": UPDATE_URL,
        "XANO_PROFILE_URL": PROFILE_URL,
        "XANO_PROFILE_PASSWORD_URL": PASSWORD_URL,
    }[name]


def user(**extra):
    value = dict(
        id=22,
        name="Maria Interna",
        email="maria@example.test",
        role="FUNCIONARIO",
        status="ATIVO",
        created_at=1704067200000,
    )
    value.update(extra)
    return value


def profile(**extra):
    value = dict(
        id=10,
        name="Admin Interno",
        email="admin@example.test",
        role="ADMINISTRADOR",
        status="ATIVO",
    )
    value.update(extra)
    return value


def state(role="ADMINISTRADOR", user_id=10):
    value = app.State(_reflex_internal_init=True)
    value._auth_token = "isolated-test-token"
    value.is_authenticated = True
    value.session_status = "success"
    value.user_status = "ATIVO"
    value.user_role = role
    value.user_id = user_id
    value.user_name = "Admin Interno"
    value.user_email = "admin@example.test"
    return value


def http_error(url, code, body=""):
    return urllib.error.HTTPError(
        url, code, "error", {}, io.BytesIO(body.encode("utf-8")))


class InternalUserContractTests(unittest.TestCase):
    def test_list_parses_only_approved_fields(self):
        records = internal_user_list([user()])
        self.assertEqual(
            (records[0].id, records[0].name, records[0].email,
             records[0].role, records[0].status),
            (22, "Maria Interna", "maria@example.test", "FUNCIONARIO", "ATIVO"))
        self.assertEqual(records[0].created_at_display,
                         "01/01/2024 às 00:00 (UTC)")

    def test_record_rejects_sensitive_or_unexpected_fields(self):
        for extra in [
            {"password": "secret"},
            {"password_reset": {"token": "secret"}},
            {"account_id": 1},
            {"USER_ID": 2},
        ]:
            with self.assertRaises(ValueError):
                internal_user_record(user(**extra), detail=True)
        with self.assertRaises(ValueError):
            internal_user_record(user(role="CLIENTE"), detail=True)
        with self.assertRaises(ValueError):
            internal_user_record(user(id=True), detail=True)
        with self.assertRaises(ValueError):
            internal_user_record(user(email="invalid"), detail=True)

    def test_create_payload_validates_and_normalizes(self):
        payload = user_create_payload(
            "  Maria  ", "  MARIA@EXAMPLE.TEST ", " Senha123 ", "FUNCIONARIO")
        self.assertEqual(payload, {
            "name": "Maria",
            "email": "maria@example.test",
            "password": "Senha123",
            "role": "FUNCIONARIO",
        })
        for values in [
            ("", "maria@example.test", "Senha123", "FUNCIONARIO"),
            ("Maria", "invalid", "Senha123", "FUNCIONARIO"),
            ("Maria", "maria@example.test", "curta1", "FUNCIONARIO"),
            ("Maria", "maria@example.test", "semnumero", "FUNCIONARIO"),
            ("Maria", "maria@example.test", "Senha123", "CLIENTE"),
        ]:
            with self.assertRaises(ValueError):
                user_create_payload(*values)

    def test_update_payload_only_returns_changes(self):
        self.assertEqual(user_update_payload(
            "Maria", "maria@example.test", "FUNCIONARIO", "ATIVO",
            current_name="Maria", current_email="maria@example.test",
            current_role="FUNCIONARIO", current_status="ATIVO"), {})
        self.assertEqual(user_update_payload(
            "Maria Nova", "", "ADMINISTRADOR", "INATIVO",
            current_name="Maria", current_email="maria@example.test",
            current_role="FUNCIONARIO", current_status="ATIVO"), {
                "name": "Maria Nova",
                "role": "ADMINISTRADOR",
                "status": "INATIVO",
            })

    def test_profile_payload_never_accepts_privileged_fields(self):
        self.assertEqual(profile_update_payload(
            "Admin Novo", "NOVO@EXAMPLE.TEST",
            current_name="Admin", current_email="admin@example.test"), {
                "name": "Admin Novo",
                "email": "novo@example.test",
            })
        self.assertEqual(profile_update_payload(
            "", "", current_name="Admin",
            current_email="admin@example.test"), {})
        for name, email in [("x" * 301, ""), ("", "invalid")]:
            with self.assertRaises(ValueError):
                profile_update_payload(
                    name, email, current_name="Admin",
                    current_email="admin@example.test")

    def test_password_payload_requires_current_and_matching_new_password(self):
        self.assertEqual(password_change_payload(
            "SenhaAtual1", "NovaSenha2", "NovaSenha2"), {
                "current_password": "SenhaAtual1",
                "new_password": "NovaSenha2",
                "confirm_password": "NovaSenha2",
            })
        for current, new, confirm in [
            ("", "NovaSenha2", "NovaSenha2"),
            ("SenhaAtual1", "curta1", "curta1"),
            ("SenhaAtual1", "NovaSenha2", "OutraSenha2"),
            ("SenhaAtual1", "SenhaAtual1", "SenhaAtual1"),
        ]:
            with self.assertRaises(ValueError):
                password_change_payload(current, new, confirm)

    def test_status_payload_accepts_only_known_values(self):
        self.assertEqual(user_status_payload("INATIVO"), {"status": "INATIVO"})
        with self.assertRaises(ValueError):
            user_status_payload("PENDENTE")


class InternalUserStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_administrator_loads_internal_users(self):
        value = state()
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=[user()])) as request:
            await app.State.load_internal_users.fn(value)

        request.assert_awaited_once()
        self.assertEqual(request.await_args.args[0], USERS_URL)
        self.assertEqual(len(value.internal_users), 1)
        self.assertFalse(value.internal_users_loading)
        self.assertEqual(value.internal_users_message, "")

    async def test_employee_cannot_load_users(self):
        value = state("FUNCIONARIO")
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.load_internal_users.fn(value)

        request.assert_not_awaited()
        self.assertEqual(value.internal_users, [])

    async def test_create_user_sends_initial_password_and_reloads(self):
        value = state()
        created = user(id=23, name="Nova Pessoa", email="nova@example.test")
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(side_effect=[created, [created]])) as request:
            await app.State.save_internal_user.fn(value, {
                "name": "  Nova Pessoa ",
                "email": " NOVA@EXAMPLE.TEST ",
                "password": "Senha123",
                "role": "FUNCIONARIO",
            })

        first = request.await_args_list[0]
        self.assertEqual(first.args[0], USERS_URL)
        self.assertEqual(first.kwargs["method"], "POST")
        self.assertEqual(first.kwargs["payload"], {
            "name": "Nova Pessoa",
            "email": "nova@example.test",
            "password": "Senha123",
            "role": "FUNCIONARIO",
        })
        self.assertEqual(len(value.internal_users), 1)
        self.assertEqual(value.internal_users_feedback,
                         "Usuário interno criado com sucesso.")
        self.assertEqual(value.internal_user_editing_id, 0)

    async def test_edit_other_user_sends_partial_update(self):
        value = state()
        value.internal_users = [internal_user_record(user(), detail=True)]
        value.internal_user_editing_id = 22
        updated = user(status="INATIVO")
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(side_effect=[updated, [updated]])) as request:
            await app.State.save_internal_user.fn(value, {
                "name": "Maria Interna",
                "email": "maria@example.test",
                "role": "FUNCIONARIO",
                "status": "INATIVO",
            })

        first = request.await_args_list[0]
        self.assertEqual(first.args[0], UPDATE_URL.replace("{user_id}", "22"))
        self.assertEqual(first.kwargs["method"], "PATCH")
        self.assertEqual(first.kwargs["payload"], {"status": "INATIVO"})
        self.assertEqual(value.internal_users[0].status, "INATIVO")
        self.assertEqual(value.internal_users_feedback,
                         "Usuário interno atualizado com sucesso.")

    async def test_administrator_cannot_change_own_role_locally(self):
        value = state()
        value.internal_users = [internal_user_record(
            user(id=10, name="Admin Interno", email="admin@example.test",
                 role="ADMINISTRADOR"), detail=True)]
        value.internal_user_editing_id = 10
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.save_internal_user.fn(value, {
                "name": "Admin Interno",
                "email": "admin@example.test",
                "role": "FUNCIONARIO",
                "status": "ATIVO",
            })

        request.assert_not_awaited()
        self.assertTrue(value.internal_users_feedback_error)
        self.assertIn("próprio perfil", value.internal_users_feedback)

    async def test_status_change_requires_confirmation(self):
        value = state()
        value.internal_users = [internal_user_record(user(), detail=True)]
        app.State.request_internal_user_status_change.fn(value, 22, "INATIVO")
        self.assertEqual(value.internal_user_status_confirmation_id, 22)
        self.assertEqual(value.internal_user_status_confirmation_status, "INATIVO")
        self.assertIn("Confirme a inativação", value.internal_users_feedback)

        updated = user(status="INATIVO")
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(side_effect=[updated, [updated]])) as request:
            await app.State.confirm_internal_user_status_change.fn(value)

        self.assertEqual(request.await_args_list[0].kwargs["payload"],
                         {"status": "INATIVO"})
        self.assertIn("histórico foi preservado", value.internal_users_feedback)

    async def test_self_status_change_is_blocked(self):
        value = state()
        value.internal_users = [internal_user_record(
            user(id=10, role="ADMINISTRADOR"), detail=True)]
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            app.State.request_internal_user_status_change.fn(value, 10, "INATIVO")
            await app.State.confirm_internal_user_status_change.fn(value)

        request.assert_not_awaited()
        self.assertEqual(value.internal_user_status_confirmation_id, 0)
        self.assertIn("próprio status", value.internal_users_feedback)

    async def test_duplicate_email_error_is_mapped(self):
        value = state()
        value.internal_users = [internal_user_record(user(), detail=True)]
        value.internal_user_editing_id = 22
        error = http_error(
            UPDATE_URL.replace("{user_id}", "22"), 400,
            '{"message":"An internal user with this email already exists."}')
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(side_effect=error)):
            await app.State.save_internal_user.fn(value, {
                "name": "Maria Interna",
                "email": "outra@example.test",
                "role": "FUNCIONARIO",
                "status": "ATIVO",
            })

        self.assertTrue(value.internal_users_feedback_error)
        self.assertIn("Já existe um usuário interno", value.internal_users_feedback)

    async def test_profile_update_refreshes_identity(self):
        value = state()
        updated = profile(name="Admin Novo", email="novo@example.test")
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value=updated)) as request:
            await app.State.save_internal_profile.fn(value, {
                "name": "Admin Novo",
                "email": "novo@example.test",
            })

        self.assertEqual(request.await_args.args[0], PROFILE_URL)
        self.assertEqual(request.await_args.kwargs["method"], "PATCH")
        self.assertEqual(value.user_name, "Admin Novo")
        self.assertEqual(value.user_email, "novo@example.test")
        self.assertEqual(value.internal_profile_name, "Admin Novo")
        self.assertEqual(value.internal_profile_feedback,
                         "Perfil atualizado com sucesso.")

    async def test_profile_password_success_clears_fields(self):
        value = state()
        value.internal_profile_password_current = "SenhaAtual1"
        value.internal_profile_password_new = "NovaSenha2"
        value.internal_profile_password_confirm = "NovaSenha2"
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value={"updated": True})) as request:
            await app.State.change_internal_profile_password.fn(value, {
                "current_password": "SenhaAtual1",
                "new_password": "NovaSenha2",
                "confirm_password": "NovaSenha2",
            })

        self.assertEqual(request.await_args.args[0], PASSWORD_URL)
        self.assertEqual(request.await_args.kwargs["method"], "POST")
        self.assertEqual(
            (value.internal_profile_password_current,
             value.internal_profile_password_new,
             value.internal_profile_password_confirm), ("", "", ""))
        self.assertEqual(value.internal_profile_feedback,
                         "Senha alterada com sucesso.")

    async def test_profile_password_rejects_wrong_current_password(self):
        value = state()
        value.internal_profile_password_current = "Errada123"
        value.internal_profile_password_new = "NovaSenha2"
        value.internal_profile_password_confirm = "NovaSenha2"
        error = http_error(
            PASSWORD_URL, 400,
            '{"message":"The current password is incorrect."}')
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(side_effect=error)):
            await app.State.change_internal_profile_password.fn(value, {
                "current_password": "Errada123",
                "new_password": "NovaSenha2",
                "confirm_password": "NovaSenha2",
            })

        self.assertTrue(value.internal_profile_feedback_error)
        self.assertEqual(value.internal_profile_feedback, "Senha atual incorreta.")
        self.assertEqual(value.internal_profile_password_current, "Errada123")

    async def test_profile_password_local_validation_never_requests(self):
        for form in [
            {"current_password": "", "new_password": "NovaSenha2",
             "confirm_password": "NovaSenha2"},
            {"current_password": "SenhaAtual1", "new_password": "curta1",
             "confirm_password": "curta1"},
            {"current_password": "SenhaAtual1", "new_password": "NovaSenha2",
             "confirm_password": "OutraSenha2"},
            {"current_password": "SenhaAtual1", "new_password": "SenhaAtual1",
             "confirm_password": "SenhaAtual1"},
        ]:
            value = state()
            with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
                await app.State.change_internal_profile_password.fn(value, form)
            request.assert_not_awaited()
            self.assertTrue(value.internal_profile_feedback_error)


class InternalUserScriptTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_group_and_all_endpoints_exist(self):
        self.assertIn('api_group "Voltix Internal Users"',
                      self.read("api_group.xs"))
        for relative in [
            "users_GET.xs", "users_POST.xs", "user/user_id_PATCH.xs",
            "profile_PATCH.xs", "profile/password_POST.xs",
        ]:
            content = self.read(relative)
            self.assertIn('api_group = "Voltix Internal Users"', content)
            self.assertIn('auth = "user"', content)

    def test_no_user_deletion_exists(self):
        for path in ROOT.rglob("*.xs"):
            self.assertNotIn("db.del user", path.read_text(encoding="utf-8"))

    def test_authorization_precedes_business_reads_and_writes(self):
        for relative, marker in [
            ("users_GET.xs", "db.query user"),
            ("users_POST.xs", "db.add user"),
            ("user/user_id_PATCH.xs", "db.edit user"),
            ("profile_PATCH.xs", "db.edit user"),
            ("profile/password_POST.xs", "db.edit user"),
        ]:
            content = self.read(relative)
            guard = content.index('role == "ADMINISTRADOR"')
            business = content.index(marker)
            self.assertLess(guard, business, relative)

    def test_list_uses_bounded_allowlist_and_management_guards(self):
        content = self.read("users_GET.xs")
        for field in ["id", "name", "email", "role", "status", "created_at"]:
            self.assertIn(field, content)
        for secret in ["password", "password_reset", "account_id"]:
            self.assertNotIn(secret, content)
        self.assertIn('sort = {name: "asc", id: "asc"}', content)

    def test_creation_requires_unique_email_and_hides_credentials(self):
        content = self.read("users_POST.xs")
        self.assertIn("db.query user", content)
        self.assertIn('error_type = "badrequest"', content)
        self.assertIn('status  : "ATIVO"', content)
        response = content[content.index("response = {"):]
        for secret in ["password", "password_reset", "account_id"]:
            self.assertNotIn(secret, response)

    def test_patch_protects_self_and_last_active_administrator(self):
        content = self.read("user/user_id_PATCH.xs")
        self.assertIn("own role or status", content)
        self.assertIn("At least one active administrator must remain", content)
        self.assertLess(content.index("own role or status"),
                        content.index("db.edit user"))
        self.assertLess(content.index("At least one active administrator must remain"),
                        content.index("db.edit user"))
        input_block = content[content.index("input {"):content.index("stack {")]
        self.assertNotIn("password", input_block)
        response = content[content.index("response = {"):]
        self.assertNotIn("password", response)

    def test_profile_cannot_change_privileged_fields(self):
        content = self.read("profile_PATCH.xs")
        input_block = content[content.index("input {"):content.index("stack {")]
        self.assertNotIn("role", input_block)
        self.assertNotIn("status", input_block)
        self.assertNotIn("password", input_block)
        self.assertNotIn("account_id", input_block)

    def test_password_change_checks_current_password(self):
        content = self.read("profile/password_POST.xs")
        self.assertIn("security.check_password", content)
        self.assertIn("current_password", content)
        self.assertIn("new_password", content)
        self.assertIn("confirm_password", content)
        response = content[content.index("response = {"):]
        self.assertNotIn("password", response)
        self.assertIn("updated: true", response)

    def test_text_password_inputs_do_not_use_password_only_filters(self):
        for relative, field in [
            ("users_POST.xs", "password"),
            ("profile/password_POST.xs", "new_password"),
        ]:
            content = self.read(relative)
            self.assertNotIn("minAlpha", content, relative)
            self.assertNotIn("minDigit", content, relative)
            self.assertIn(f"text {field} filters=min:8", content, relative)
            self.assertIn('regex_test:"[A-Za-z]"', content, relative)
            self.assertIn('regex_test:"[0-9]"', content, relative)
            strength = content.index("regex_test")
            write = content.index("db.add user" if relative == "users_POST.xs"
                                  else "db.edit user")
            self.assertLess(strength, write, relative)

    def test_user_table_password_column_keeps_password_filters(self):
        table = Path("xano/table/user.xs").read_text(encoding="utf-8")
        self.assertIn("password filters=min:8|minAlpha:1|minDigit:1", table)


if __name__ == "__main__":
    unittest.main()
