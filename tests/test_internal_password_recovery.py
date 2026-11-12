import io
import unittest
import urllib.error
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import voltix.voltix as app
from voltix.internal_password_recovery import (
    recovery_confirm_payload,
    recovery_confirm_result,
    recovery_email_payload,
    recovery_request_result,
)

REQUEST_URL = "https://example.test/password-recovery/request"
CONFIRM_URL = "https://example.test/password-recovery/confirm"
ROOT = Path("xano/api/internal_password_recovery")
SOURCE = Path("voltix/voltix.py")
TOKEN = "token-value-1234567890123"
GENERIC_REQUEST_MESSAGE = (
    "Se o e-mail estiver cadastrado, enviaremos as instruções."
)


def urls(name):
    return {
        app.XANO_PASSWORD_RESET_REQUEST_URL_ENV: REQUEST_URL,
        app.XANO_PASSWORD_RESET_CONFIRM_URL_ENV: CONFIRM_URL,
    }[name]


def state():
    return app.State(_reflex_internal_init=True)


def http_error(url, code, body=""):
    return urllib.error.HTTPError(
        url, code, "error", {}, io.BytesIO(body.encode("utf-8")))


class InternalRecoveryContractTests(unittest.TestCase):
    def test_email_payload_normalizes_and_validates(self):
        self.assertEqual(
            recovery_email_payload("  MARIA@EXAMPLE.TEST "),
            {"email": "maria@example.test"})
        for value in ["", "invalid", "a@b", "maria@example", "x" * 255 + "@example.test",
                      123, None, ["a@example.test"]]:
            with self.assertRaises(ValueError):
                recovery_email_payload(value)

    def test_confirm_payload_builds_consistent_payload(self):
        self.assertEqual(
            recovery_confirm_payload(
                "  MARIA@EXAMPLE.TEST ", "  " + TOKEN + "  ",
                "SenhaNova1", " SenhaNova1 "),
            {
                "email": "maria@example.test",
                "token": TOKEN,
                "password": "SenhaNova1",
                "confirm_password": "SenhaNova1",
            })
        for values in [
            ("maria@example.test", "short", "SenhaNova1", "SenhaNova1"),
            ("maria@example.test", "x" * 129, "SenhaNova1", "SenhaNova1"),
            ("maria@example.test", "token com espacos 12345678", "SenhaNova1", "SenhaNova1"),
            ("maria@example.test", TOKEN, "curta1", "curta1"),
            ("maria@example.test", TOKEN, "SemNumero", "SemNumero"),
            ("maria@example.test", TOKEN, "SenhaNova1", "OutraSenha2"),
            ("invalid", TOKEN, "SenhaNova1", "SenhaNova1"),
        ]:
            with self.assertRaises(ValueError):
                recovery_confirm_payload(*values)

    def test_request_result_only_returns_the_generic_message(self):
        self.assertEqual(
            recovery_request_result({"message": "qualquer outro texto"}),
            GENERIC_REQUEST_MESSAGE)
        for payload in [None, [], {}, {"message": ""}, {"message": 1}]:
            with self.assertRaises(ValueError):
                recovery_request_result(payload)

    def test_confirm_result_requires_updated_true(self):
        self.assertTrue(recovery_confirm_result({"updated": True}))
        self.assertFalse(recovery_confirm_result({"updated": False}))
        self.assertFalse(recovery_confirm_result({"updated": "true"}))
        for payload in [None, [], {}, {"updated": 1}]:
            if isinstance(payload, dict):
                self.assertFalse(recovery_confirm_result(payload))
            else:
                with self.assertRaises(ValueError):
                    recovery_confirm_result(payload)


class InternalRecoveryStateTests(unittest.IsolatedAsyncioTestCase):
    async def test_request_posts_email_and_shows_the_generic_message(self):
        value = state()
        value.internal_recovery_email = "Maria@Example.test"
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value={"message": "magic link sent"})) as request:
            await app.State.request_internal_password_recovery.fn(
                value, {"email": " Maria@Example.test "})

        request.assert_awaited_once()
        self.assertEqual(request.await_args.args[0], REQUEST_URL)
        self.assertEqual(request.await_args.kwargs["method"], "POST")
        self.assertEqual(request.await_args.kwargs["payload"],
                         {"email": "maria@example.test"})
        self.assertTrue(value.internal_recovery_done)
        self.assertEqual(value.internal_recovery_feedback, GENERIC_REQUEST_MESSAGE)
        self.assertFalse(value.internal_recovery_feedback_error)
        self.assertEqual(value.internal_recovery_email, "")
        self.assertFalse(value.internal_recovery_loading)

    async def test_request_http_errors_never_claim_delivery(self):
        for code in (400, 401, 403, 429, 500):
            value = state()
            value.internal_recovery_email = "maria@example.test"
            error = http_error(REQUEST_URL, code)
            with patch.object(app, "_required_environment_url", side_effect=urls), \
                    patch.object(app, "_server_side_xano_request",
                                 AsyncMock(side_effect=error)):
                await app.State.request_internal_password_recovery.fn(
                    value, {"email": "maria@example.test"})

            self.assertFalse(value.internal_recovery_done, code)
            self.assertTrue(value.internal_recovery_feedback_error, code)
            self.assertEqual(value.internal_recovery_feedback,
                             "Não foi possível enviar as instruções. Tente novamente.")
            self.assertEqual(value.internal_recovery_email, "maria@example.test")
            self.assertFalse(value.internal_recovery_loading)
            error.close()

    async def test_request_local_validation_never_requests(self):
        for form in [{}, {"email": "  "}, {"email": "invalid"}, {"email": "a@b"}]:
            value = state()
            with patch.object(app, "_server_side_xano_request",
                              AsyncMock()) as request:
                await app.State.request_internal_password_recovery.fn(value, form)
            request.assert_not_awaited()
            self.assertTrue(value.internal_recovery_feedback_error)
            self.assertEqual(value.internal_recovery_feedback, "Informe um e-mail válido.")

    async def test_confirm_success_clears_the_form(self):
        value = state()
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value={"updated": True})) as request:
            await app.State.submit_internal_password_reset.fn(value, {
                "email": "maria@example.test",
                "token": TOKEN,
                "password": "SenhaNova1",
                "confirm_password": "SenhaNova1",
            })

        self.assertEqual(request.await_args.args[0], CONFIRM_URL)
        self.assertEqual(request.await_args.kwargs["method"], "POST")
        self.assertEqual(request.await_args.kwargs["payload"], {
            "email": "maria@example.test",
            "token": TOKEN,
            "password": "SenhaNova1",
            "confirm_password": "SenhaNova1",
        })
        self.assertTrue(value.internal_reset_done)
        self.assertEqual((value.internal_reset_email, value.internal_reset_token,
                          value.internal_reset_password, value.internal_reset_confirm),
                         ("", "", "", ""))
        self.assertEqual(value.internal_reset_feedback,
                         "Senha redefinida com sucesso. Entre com a nova senha.")
        self.assertFalse(value.internal_reset_feedback_error)
        self.assertFalse(value.internal_reset_loading)

    async def test_confirm_400_maps_to_the_generic_error_and_keeps_fields(self):
        value = state()
        value.internal_reset_email = "maria@example.test"
        value.internal_reset_token = TOKEN
        value.internal_reset_password = "SenhaNova1"
        value.internal_reset_confirm = "SenhaNova1"
        error = http_error(
            CONFIRM_URL, 400,
            '{"message":"Link inválido ou expirado."}')
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(side_effect=error)):
            await app.State.submit_internal_password_reset.fn(value, {
                "email": "maria@example.test",
                "token": TOKEN,
                "password": "SenhaNova1",
                "confirm_password": "SenhaNova1",
            })

        self.assertFalse(value.internal_reset_done)
        self.assertTrue(value.internal_reset_feedback_error)
        self.assertEqual(value.internal_reset_feedback,
                         "Link inválido ou expirado.")
        self.assertEqual(
            (value.internal_reset_email, value.internal_reset_token,
             value.internal_reset_password, value.internal_reset_confirm),
            ("maria@example.test", TOKEN, "SenhaNova1", "SenhaNova1"))
        error.close()

    async def test_confirm_unexpected_response_never_claims_success(self):
        value = state()
        with patch.object(app, "_required_environment_url", side_effect=urls), \
                patch.object(app, "_server_side_xano_request",
                             AsyncMock(return_value={"updated": False})):
            await app.State.submit_internal_password_reset.fn(value, {
                "email": "maria@example.test",
                "token": TOKEN,
                "password": "SenhaNova1",
                "confirm_password": "SenhaNova1",
            })

        self.assertFalse(value.internal_reset_done)
        self.assertTrue(value.internal_reset_feedback_error)
        self.assertEqual(value.internal_reset_feedback,
                         "Não foi possível redefinir a senha. Tente novamente.")

    async def test_confirm_local_validation_never_requests(self):
        for form in [
            {"email": "invalid", "token": TOKEN,
             "password": "SenhaNova1", "confirm_password": "SenhaNova1"},
            {"email": "maria@example.test", "token": "short",
             "password": "SenhaNova1", "confirm_password": "SenhaNova1"},
            {"email": "maria@example.test", "token": TOKEN,
             "password": "curta1", "confirm_password": "curta1"},
            {"email": "maria@example.test", "token": TOKEN,
             "password": "SenhaNova1", "confirm_password": "OutraSenha2"},
        ]:
            value = state()
            with patch.object(app, "_server_side_xano_request",
                              AsyncMock()) as request:
                await app.State.submit_internal_password_reset.fn(value, form)
            request.assert_not_awaited()
            self.assertTrue(value.internal_reset_feedback_error)
            self.assertFalse(value.internal_reset_done)

    def test_enter_internal_reset_reads_and_sanitizes_query_parameters(self):
        value = SimpleNamespace(
            router=SimpleNamespace(url=SimpleNamespace(query_parameters={
                "email": "  Maria@Example.test  ",
                "token": "  " + TOKEN + "  ",
            })),
        )
        app.State.enter_internal_reset.fn(value)

        self.assertEqual(value.internal_reset_email, "Maria@Example.test")
        self.assertEqual(value.internal_reset_token, TOKEN)
        self.assertEqual(value.internal_reset_password, "")
        self.assertEqual(value.internal_reset_confirm, "")
        self.assertFalse(value.internal_reset_done)

    def test_enter_internal_reset_rejects_unexpected_query_values(self):
        for query in [
            {"email": ["maria@example.test"], "token": TOKEN},
            {"email": "x" * 500, "token": TOKEN},
            {"email": "maria@example.test", "token": "y" * 500},
        ]:
            value = SimpleNamespace(
                router=SimpleNamespace(url=SimpleNamespace(query_parameters=query)),
            )
            app.State.enter_internal_reset.fn(value)
            self.assertEqual(len(value.internal_reset_email) <= 254, True)
            self.assertEqual(len(value.internal_reset_token) <= 128, True)
            self.assertNotIn("[", value.internal_reset_token)


class InternalRecoveryScriptTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_group_and_endpoints_exist_and_are_public(self):
        group = self.read("api_group.xs")
        self.assertIn('api_group "Voltix Internal Password Recovery"', group)
        self.assertIn('canonical = "voltix-internal-password-recovery"', group)
        self.assertIn('voltix:internal-password-recovery', group)
        for relative in ["request_POST.xs", "confirm_POST.xs"]:
            content = self.read(relative)
            self.assertIn(
                'api_group = "Voltix Internal Password Recovery"', content)
            self.assertNotIn('auth = "user"', content)
            self.assertNotIn("security.create_auth_token", content)

    def test_request_is_generic_and_guarded(self):
        content = self.read("request_POST.xs")
        self.assertIn(GENERIC_REQUEST_MESSAGE, content)
        self.assertIn("security.create_uuid", content)
        self.assertIn("add_secs_to_timestamp:(3600|to_int)", content)
        self.assertIn('$user.status == "ATIVO"', content)
        self.assertIn('$user.role == "FUNCIONARIO"', content)
        self.assertIn('$user.role == "ADMINISTRADOR"', content)
        self.assertIn("util.send_email", content)
        self.assertIn("voltix_app_url", content)
        self.assertIn("interno/redefinir-senha", content)
        self.assertNotIn("db.del", content)
        guard = content.index('$user.status == "ATIVO"')
        edit = content.index("db.edit user")
        self.assertLess(guard, edit)
        response = content[content.index("response = {"):]
        response = response.split("tags =", 1)[0]
        for secret in ["token", "reset_link", "password:", "password :"]:
            self.assertNotIn(secret, response)

    def test_confirm_validates_and_consumes_a_single_use_token(self):
        content = self.read("confirm_POST.xs")
        for fragment in [
            "security.check_password",
            "Link inválido ou expirado.",
            '$user.status == "ATIVO"',
            '$user.role == "FUNCIONARIO"',
            '$user.role == "ADMINISTRADOR"',
            "password_reset.used",
            "expiration > now",
            "enforce_hidden_fields = false",
        ]:
            self.assertIn(fragment, content)
        self.assertNotIn("security.create_auth_token", content)
        self.assertNotIn("db.del", content)
        data = content[content.index("data = {"):content.index("} as $updated_user")]
        self.assertIn("used", data)
        self.assertIn("true", data)
        response = content[content.index("response = {"):]
        response = response.split("tags =", 1)[0]
        self.assertIn("updated: true", response)
        for secret in ["password:", "password :", "token:", "token :", "hash"]:
            self.assertNotIn(secret, response)

    def test_no_template_or_account_scope_dependencies(self):
        for path in ROOT.rglob("*.xs"):
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("account_id", content)
            self.assertNotIn("magic-link-login", content)
            self.assertNotIn("Getting Started Template", content)
            self.assertNotIn("debug.log", content)
            self.assertNotIn("db.del", content)


class InternalRecoveryFrontendTests(unittest.TestCase):
    def read(self, relative):
        return Path(relative).read_text(encoding="utf-8")

    def test_recovery_pages_are_registered(self):
        source = self.read(SOURCE)
        self.assertIn('route="/interno/recuperar-senha"', source)
        self.assertIn('route="/interno/redefinir-senha"', source)
        self.assertIn("on_load=State.enter_internal_reset", source)
        self.assertIn("internal_recovery_request_page,", source)
        self.assertIn("internal_password_reset_page,", source)

    def test_reset_page_renders_the_token_as_a_password_field(self):
        source = self.read(SOURCE)
        token_block = source[source.index('id="internal-reset-token"'):
                             source.index('id="internal-reset-password"')]
        self.assertIn('type="password"', token_block)
        self.assertIn("State.internal_reset_token", token_block)
        self.assertNotIn(">Token<", token_block)

    def test_recovery_css_classes_are_scoped(self):
        css = self.read("assets/voltix-internal.css")
        self.assertIn(".vx-internal-login__forgot", css)
        self.assertIn(".vx-internal-login__back", css)

    def test_environment_contract_is_documented(self):
        env_example = self.read(".env.example")
        self.assertIn("XANO_PASSWORD_RESET_REQUEST_URL", env_example)
        self.assertIn("XANO_PASSWORD_RESET_CONFIRM_URL", env_example)


if __name__ == "__main__":
    unittest.main()
