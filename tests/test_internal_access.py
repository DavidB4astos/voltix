import unittest
import urllib.error
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import voltix.voltix as app

LOGIN_URL = "https://example.test/auth/login"
ME_URL = "https://example.test/auth/me"
ACCESS_URL = "https://example.test/auth/internal-access"


def urls(name):
    return {
        app.XANO_LOGIN_URL_ENV: LOGIN_URL,
        app.XANO_ME_URL_ENV: ME_URL,
        app.XANO_INTERNAL_ACCESS_URL_ENV: ACCESS_URL,
    }[name]


def identity(**extra):
    value = {
        "id": 7,
        "name": "Interno Teste",
        "email": "interno@example.test",
        "role": "FUNCIONARIO",
        "status": "ATIVO",
    }
    value.update(extra)
    return value


class InternalLoginTests(unittest.IsolatedAsyncioTestCase):
    def state(self):
        return app.State(_reflex_internal_init=True)

    async def test_valid_login_stores_token_and_identity(self):
        state = self.state()
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value={"authToken": " token-value ", "user_id": 7})) as request, \
                patch("urllib.request.urlopen",
                      side_effect=AssertionError("real network must not be used")):
            await app.State.login.fn(state, "interno@example.test", "senha")

        request.assert_awaited_once()
        self.assertEqual(request.await_args.args[0], LOGIN_URL)
        self.assertEqual(request.await_args.kwargs["method"], "POST")
        self.assertEqual(request.await_args.kwargs["payload"],
                         {"email": "interno@example.test", "password": "senha"})
        self.assertEqual(state._auth_token, "token-value")
        self.assertEqual(state.user_id, 7)
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.login_status, "success")
        self.assertFalse(state.login_loading)

    async def test_rejected_login_clears_authentication(self):
        state = self.state()
        error = urllib.error.HTTPError(LOGIN_URL, 401, "denied", {}, None)
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.login.fn(state, "interno@example.test", "errada")

        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")
        self.assertIsNone(state.user_id)
        self.assertEqual(state.login_status, "error")
        self.assertIn("Não foi possível autenticar", state.login_message)
        error.close()

    async def test_malformed_login_responses_are_rejected(self):
        for response in [None, {}, {"authToken": "", "user_id": 1},
                         {"authToken": "abc"}, {"authToken": "abc", "user_id": "1"},
                         {"authToken": "abc", "user_id": None}]:
            state = self.state()
            with patch.object(app, "_required_environment_url", side_effect=urls), \
                    patch.object(app, "_server_side_xano_request", AsyncMock(return_value=response)):
                await app.State.login.fn(state, "interno@example.test", "senha")
            self.assertFalse(state.is_authenticated)
            self.assertEqual(state._auth_token, "")
            self.assertIsNone(state.user_id)

    async def test_missing_configuration_never_requests(self):
        state = self.state()

        def missing(name):
            raise ValueError(f"Missing required environment variable: {name}.")
        with patch.object(app, "_required_environment_url", side_effect=missing), \
                patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.login.fn(state, "interno@example.test", "senha")

        request.assert_not_awaited()
        self.assertEqual(state.login_status, "error")
        self.assertFalse(state.is_authenticated)

    async def test_submit_login_requires_both_fields(self):
        for form in [{}, {"email": "interno@example.test"}, {"password": "senha"},
                     {"email": "  ", "password": "senha"}]:
            state = self.state()
            with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
                await app.State.submit_login.fn(state, form)
            request.assert_not_awaited()
            self.assertEqual(state.login_status, "error")
            self.assertEqual(state.login_message, "Informe e-mail e senha.")

    async def test_submit_login_delegates_valid_form(self):
        state = self.state()
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value={"authToken": "token-value", "user_id": 7})) as request:
            await app.State.submit_login.fn(
                state, {"email": " interno@example.test ", "password": "senha"})

        self.assertEqual(request.await_args.kwargs["payload"]["email"], "interno@example.test")
        self.assertTrue(state.is_authenticated)


class InternalSessionTests(unittest.IsolatedAsyncioTestCase):
    def state(self):
        return app.State(_reflex_internal_init=True)

    async def test_valid_session_stores_identity(self):
        state = self.state()
        state._auth_token = "token-value"
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(side_effect=[identity(), {"authorized": True}])) as request:
            await app.State.validate_session.fn(state)

        self.assertEqual(request.await_count, 2)
        self.assertEqual(request.await_args_list[0].args[0], ME_URL)
        self.assertEqual(request.await_args_list[1].args[0], ACCESS_URL)
        self.assertEqual(request.await_args_list[0].kwargs["authorization"], "Bearer token-value")
        self.assertTrue(state.is_authenticated)
        self.assertEqual(state.session_status, "success")
        self.assertEqual((state.user_id, state.user_name, state.user_email,
                          state.user_role, state.user_status),
                         (7, "Interno Teste", "interno@example.test", "FUNCIONARIO", "ATIVO"))

    async def test_missing_token_clears_without_request(self):
        state = self.state()
        with patch.object(app, "_server_side_xano_request", AsyncMock()) as request:
            await app.State.validate_session.fn(state)
        request.assert_not_awaited()
        self.assertFalse(state.is_authenticated)
        self.assertEqual(state.session_status, "error")

    async def test_invalid_identities_clear_the_session(self):
        for payload in [identity(role="CLIENTE"), identity(role="ADMIN"),
                        identity(status="INATIVO"), identity(status="ATIVO "),
                        identity(name=""), identity(email=""), identity(id="7"),
                        identity(id=True), [], None]:
            state = self.state()
            state._auth_token = "token-value"
            with patch.object(app, "_required_environment_url", side_effect=urls), \
                    patch.object(app, "_server_side_xano_request",
                                 AsyncMock(return_value=payload)):
                await app.State.validate_session.fn(state)
            self.assertFalse(state.is_authenticated)
            self.assertEqual(state._auth_token, "")
            self.assertEqual(state.session_status, "error")
            self.assertIn("Não foi possível validar a sessão.", state.session_message)

    async def test_rejected_protected_area_clears_the_session(self):
        for response in [{"authorized": False}, {"authorized": "true"}, {}]:
            state = self.state()
            state._auth_token = "token-value"
            with patch.object(app, "_required_environment_url", side_effect=urls), \
                    patch.object(app, "_server_side_xano_request",
                                 AsyncMock(side_effect=[identity(), response])):
                await app.State.validate_session.fn(state)
            self.assertFalse(state.is_authenticated)
            self.assertEqual(state.session_status, "error")

    async def test_http_failure_clears_the_session(self):
        state = self.state()
        state._auth_token = "token-value"
        error = urllib.error.HTTPError(ME_URL, 401, "denied", {}, None)
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request", AsyncMock(side_effect=error)):
            await app.State.validate_session.fn(state)

        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")
        self.assertEqual(state.user_role, "")
        error.close()

    def generations(self, state):
        return (state._internal_customers_generation, state._internal_attendances_generation,
                state._internal_orders_generation, state._internal_dashboard_generation)

    async def test_identity_change_clears_internal_data(self):
        state = self.state()
        state._auth_token = "token-value"
        state.user_id = 99
        state.user_role = "FUNCIONARIO"
        before = self.generations(state)
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(side_effect=[identity(), {"authorized": True}])):
            await app.State.validate_session.fn(state)

        self.assertEqual(self.generations(state), tuple(value + 1 for value in before))
        self.assertEqual(state.user_id, 7)

    async def test_same_identity_keeps_internal_data(self):
        state = self.state()
        state._auth_token = "token-value"
        state.user_id = 7
        state.user_role = "FUNCIONARIO"
        before = self.generations(state)
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(side_effect=[identity(), {"authorized": True}])):
            await app.State.validate_session.fn(state)

        self.assertEqual(self.generations(state), before)

    async def test_enter_internal_area_only_refreshes_products_for_administrator(self):
        for role, refreshed in [("ADMINISTRADOR", True), ("FUNCIONARIO", False)]:
            state = SimpleNamespace(session_status="success", user_role=role,
                                    user_status="ATIVO",
                                    validate_session=AsyncMock(),
                                    _refresh_products=AsyncMock())
            await app.State.enter_internal_area.fn(state)
            self.assertEqual(state._refresh_products.await_count, 1 if refreshed else 0)

    async def test_logout_removes_the_session(self):
        state = self.state()
        state._auth_token = "token-value"
        state.is_authenticated = True
        state.user_id = 7
        state.user_role = "ADMINISTRADOR"
        state.internal_section = "dashboard"
        await app.State.logout.fn(state)

        self.assertFalse(state.is_authenticated)
        self.assertEqual(state._auth_token, "")
        self.assertIsNone(state.user_id)
        self.assertEqual(state.user_role, "")
        self.assertEqual(state.internal_section, "clientes")
        self.assertEqual(state.session_status, "idle")
        self.assertEqual(state.session_message, "Sessão encerrada.")


class InternalAccessContractTests(unittest.TestCase):
    def read(self, relative):
        return Path(relative).read_text(encoding="utf-8")

    def test_login_accepts_only_active_approved_profiles(self):
        login = self.read("xano/api/authentication/auth/login_POST.xs")
        self.assertIn('$user.role == "FUNCIONARIO"', login)
        self.assertIn('$user.role == "ADMINISTRADOR"', login)
        self.assertIn('$user.status == "ATIVO"', login)
        self.assertIn("security.check_password", login)
        self.assertIn('error_type = "accessdenied"', login)

    def test_identity_response_exposes_no_credentials(self):
        me = self.read("xano/api/authentication/auth/me_GET.xs")
        self.assertIn('output = ["id", "name", "email", "role", "status"]', me)
        self.assertNotIn("password", me.split("response =", 1)[1])
        self.assertNotIn("authToken", me.split("response =", 1)[1])
        self.assertIn('$user.role == "FUNCIONARIO"', me)
        self.assertIn('$user.role == "ADMINISTRADOR"', me)
        self.assertIn('$user.status == "ATIVO"', me)
        self.assertIn('error_type = "accessdenied"', me)

    def test_protected_access_returns_only_authorization(self):
        access = self.read("xano/api/authentication/auth/internal_access_GET.xs")
        self.assertIn("authorized: true", access)
        self.assertIn('$user.role == "FUNCIONARIO"', access)
        self.assertIn('$user.role == "ADMINISTRADOR"', access)
        self.assertIn('$user.status == "ATIVO"', access)
        self.assertIn('error_type = "accessdenied"', access)
        self.assertNotIn("password", access)
        self.assertNotIn("authToken", access)

    def test_login_page_links_internal_password_recovery(self):
        source = self.read("voltix/voltix.py")
        self.assertIn('"Esqueci minha senha"', source)
        self.assertIn("/interno/recuperar-senha", source)

    def test_no_public_internal_signup_endpoint_is_defined(self):
        auth_dir = Path("xano/api/authentication/auth")
        names = {path.name.lower() for path in auth_dir.glob("*.xs")}
        self.assertFalse(any("signup" in name or "register" in name for name in names))


if __name__ == "__main__":
    unittest.main()
