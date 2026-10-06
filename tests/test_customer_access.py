import asyncio
import os
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from urllib.error import URLError

import voltix.voltix as app


class _FakeCustomerState:
    _clear_customer_session = app.State._clear_customer_session
    _clear_customer_address_form = app.State._clear_customer_address_form
    _set_customer_profile = app.State._set_customer_profile
    _customer_request = app.State._customer_request
    _load_customer_addresses = app.State._load_customer_addresses

    _customer_auth_token = "customer-runtime-token"
    _auth_token = "internal-runtime-token"
    customer_authenticated = True
    customer_session_status = "success"
    customer_id = 17
    customer_login_status = "idle"
    customer_login_message = ""
    customer_registration_status = "idle"
    customer_registration_message = ""
    customer_session_message = ""
    customer_name = "Ada Cliente"
    customer_cpf = "11122233344"
    customer_email = "ada@example.test"
    customer_phone = "11999990000"
    customer_addresses = []
    customer_addresses_loading = False
    customer_addresses_message = ""
    customer_profile_message = ""
    customer_address_editing_id = None
    customer_address_form_cep = ""
    customer_address_form_street = ""
    customer_address_form_number = ""
    customer_address_form_complement = ""
    customer_address_form_neighborhood = ""
    customer_address_form_city = ""
    customer_address_form_state = ""
    customer_address_form_label = ""
    is_authenticated = True


class CustomerAccessTests(unittest.TestCase):
    def test_customer_payload_parsers_validate_identity_and_address_owner_fields(self):
        customer = app._customer_profile(
            {
                "id": 3,
                "nome_completo": "Ada Cliente",
                "cpf": "11122233344",
                "email": "ada@example.test",
                "telefone": None,
                "status": "ATIVO",
            }
        )
        self.assertEqual(customer.id, 3)
        self.assertEqual(customer.phone, "")

        address = app._customer_address(
            {
                "id": 8,
                "cliente_id": 3,
                "cep": None,
                "logradouro": "Rua Um",
                "numero": "10",
                "complemento": None,
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "identificacao": "Casa",
                "principal": True,
                "status": "ATIVO",
            }
        )
        self.assertEqual(address.customer_id, 3)
        self.assertTrue(address.is_primary)
        self.assertEqual(address.complement, "")
        self.assertEqual(app._customer_addresses([{
            "id": 8,
            "cliente_id": 3,
            "principal": False,
            "status": "INATIVO",
        }])[0].status, "INATIVO")

        invalid_customer = {
            "id": 3,
            "nome_completo": "Ada",
            "cpf": "11122233344",
            "email": "ada@example.test",
            "status": "INATIVO",
        }
        with self.assertRaises(ValueError):
            app._customer_profile(invalid_customer)
        with self.assertRaises(ValueError):
            app._customer_address(
                {
                    "id": 8,
                    "cliente_id": 3,
                    "principal": "true",
                    "status": "ATIVO",
                }
            )

    def test_customer_login_uses_separate_token_and_revalidates_identity(self):
        state = _FakeCustomerState()
        response = {
            "authToken": "new-customer-token",
            "customer": {
                "id": 17,
                "nome_completo": "Ada Cliente",
                "cpf": "11122233344",
                "email": "ada@example.test",
                "telefone": "",
                "status": "ATIVO",
            },
        }
        mocked_request = AsyncMock(
            side_effect=[
                response,
                response["customer"],
                [],
            ]
        )
        os.environ[app.XANO_CUSTOMER_LOGIN_URL_ENV] = (
            "https://example.invalid/api:voltix-customer/login"
        )
        os.environ[app.XANO_CUSTOMER_ME_URL_ENV] = (
            "https://example.invalid/api:voltix-customer/me"
        )
        os.environ[app.XANO_CUSTOMER_ADDRESSES_URL_ENV] = (
            "https://example.invalid/api:voltix-customer/addresses"
        )

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                await app.State.customer_login.fn(
                    state,
                    "ada@example.test",
                    "password",
                )

            self.assertTrue(state.customer_authenticated)
            self.assertEqual(state.customer_session_status, "success")
            self.assertEqual(state._customer_auth_token, "new-customer-token")
            self.assertEqual(state._auth_token, "internal-runtime-token")
            self.assertTrue(state.is_authenticated)
            self.assertEqual(
                mocked_request.call_args_list[1].kwargs["authorization"],
                "Bearer new-customer-token",
            )
            self.assertEqual(
                mocked_request.call_args_list[2].kwargs["authorization"],
                "Bearer new-customer-token",
            )

        asyncio.run(run())

    def test_invalid_customer_login_does_not_create_session(self):
        state = _FakeCustomerState()
        mocked_request = AsyncMock(return_value={"authToken": "token"})
        os.environ[app.XANO_CUSTOMER_LOGIN_URL_ENV] = (
            "https://example.invalid/customer/login"
        )

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                await app.State.customer_login.fn(state, "bad@example.test", "bad")
            self.assertFalse(state.customer_authenticated)
            self.assertEqual(state.customer_session_status, "error")
            self.assertEqual(state._customer_auth_token, "")
            self.assertEqual(state.customer_login_status, "error")

        asyncio.run(run())

    def test_customer_registration_is_server_side_and_does_not_create_a_session(self):
        state = _FakeCustomerState()
        state.customer_authenticated = False
        state._customer_auth_token = ""
        response = {
            "id": 21,
            "nome_completo": "Grace Cliente",
            "cpf": "55566677788",
            "email": "grace@example.test",
            "telefone": "",
            "status": "ATIVO",
        }
        mocked_request = AsyncMock(return_value=response)
        os.environ[app.XANO_CUSTOMER_URL_ENV] = (
            "https://example.invalid/api:legacy/cliente"
        )

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                await app.State.register_customer.fn(
                    state,
                    {
                        "nome_completo": " Grace Cliente ",
                        "cpf": " 55566677788 ",
                        "email": "grace@example.test",
                        "telefone": "",
                        "password": "secret",
                    },
                )

            self.assertEqual(mocked_request.call_args.kwargs["method"], "POST")
            self.assertEqual(
                mocked_request.call_args.kwargs["payload"]["cpf"],
                "55566677788",
            )
            self.assertNotIn("authorization", mocked_request.call_args.kwargs)
            self.assertFalse(state.customer_authenticated)
            self.assertEqual(state._customer_auth_token, "")
            self.assertEqual(state.customer_registration_status, "success")

        asyncio.run(run())

    def test_customer_profile_update_never_submits_cpf_or_credentials(self):
        state = _FakeCustomerState()
        profile = {
            "id": 17,
            "nome_completo": "Ada Atualizada",
            "cpf": "11122233344",
            "email": "ada.updated@example.test",
            "telefone": "11999990000",
            "status": "ATIVO",
        }
        state._customer_request = AsyncMock(return_value=profile)

        async def run():
            await app.State.update_customer_profile.fn(
                state,
                {
                    "nome_completo": "Ada Atualizada",
                    "email": "ada.updated@example.test",
                    "telefone": "11999990000",
                },
            )

            request = state._customer_request.call_args
            self.assertEqual(request.kwargs["method"], "PATCH")
            self.assertEqual(request.kwargs["record_id"], 17)
            self.assertEqual(
                set(request.kwargs["payload"]),
                {"nome_completo", "email", "telefone"},
            )
            self.assertEqual(state.customer_name, "Ada Atualizada")

        asyncio.run(run())

    def test_customer_requests_require_customer_session_not_internal_session(self):
        state = _FakeCustomerState()
        state._customer_auth_token = ""
        state.customer_authenticated = False
        state.customer_session_status = "idle"
        mocked_request = AsyncMock(return_value=[])
        os.environ[app.XANO_CUSTOMER_ADDRESSES_URL_ENV] = (
            "https://example.invalid/customer/addresses"
        )

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                with self.assertRaisesRegex(ValueError, "Active customer session"):
                    await app.State._customer_request(
                        state,
                        app.XANO_CUSTOMER_ADDRESSES_URL_ENV,
                    )
            mocked_request.assert_not_called()

        asyncio.run(run())

    def test_customer_address_requests_are_server_side_and_never_send_owner_id(self):
        state = _FakeCustomerState()
        created = {
            "id": 9,
            "cliente_id": 17,
            "cep": "01000000",
            "logradouro": "Rua Um",
            "numero": "10",
            "complemento": "",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": "SP",
            "identificacao": "Casa",
            "principal": False,
            "status": "ATIVO",
        }
        state._customer_request = AsyncMock(return_value=created)
        state._load_customer_addresses = AsyncMock(return_value=True)

        async def run():
            await app.State.save_customer_address.fn(
                state,
                {
                    "cep": "01000000",
                    "logradouro": "Rua Um",
                    "numero": "10",
                    "complemento": "",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "identificacao": "Casa",
                },
            )

            request = state._customer_request.call_args
            self.assertEqual(
                request.args[0],
                app.XANO_CUSTOMER_ADDRESSES_URL_ENV,
            )
            self.assertEqual(request.kwargs["method"], "POST")
            self.assertNotIn("cliente_id", request.kwargs["payload"])
            self.assertEqual(
                request.kwargs["payload"]["logradouro"],
                "Rua Um",
            )
            self.assertEqual(state.customer_addresses_message, "Endereço salvo.")

        asyncio.run(run())

    def test_address_failure_does_not_update_confirmed_list_or_claim_success(self):
        state = _FakeCustomerState()
        prior = app.CustomerAddressEntry(
            4, 17, "01000000", "Rua Antiga", "1", "", "Centro",
            "São Paulo", "SP", "Casa", True, "ATIVO"
        )
        state.customer_addresses = [prior]
        state._customer_request = AsyncMock(side_effect=URLError("network unavailable"))

        async def run():
            await app.State.save_customer_address.fn(
                state,
                {"logradouro": "Rua Nova"},
            )
            self.assertEqual(state.customer_addresses, [prior])
            self.assertIn("Não foi possível salvar", state.customer_addresses_message)

        asyncio.run(run())

    def test_customer_schema_authentication_and_legacy_routes_are_owner_scoped(self):
        client_table = Path("xano/table/cliente.xs").read_text(encoding="utf-8")
        internal_table = Path("xano/table/user.xs").read_text(encoding="utf-8")
        self.assertIn("auth = true", client_table)
        self.assertIn("int USER_ID?", client_table)
        self.assertIn("text CELULAR_CLIENT?", client_table)
        self.assertIn("text cpf filters=trim", client_table)
        self.assertIn('name: "cpf"', client_table)
        self.assertIn('name: "email"', client_table)
        self.assertIn('auth = true', internal_table)
        self.assertIn('values = ["FUNCIONARIO", "ADMINISTRADOR"]', internal_table)

        login = Path("xano/api/customer/customer_login_POST.xs").read_text(
            encoding="utf-8"
        )
        self.assertIn('table = "CLIENTE"', login)
        self.assertIn("security.check_password", login)
        self.assertIn('$customer.status == "ATIVO"', login)
        login_response = login.split("response =", 1)[1]
        self.assertNotIn("password", login_response.lower())
        identity = Path(
            "xano/api/customer/customer_me_GET.xs"
        ).read_text(encoding="utf-8")
        self.assertIn('auth = "CLIENTE"', identity)
        self.assertNotIn("password", identity.lower())
        self.assertNotIn("authToken", identity)
        registration = Path(
            "xano/api/db_xano_bastos/cliente_POST.xs"
        ).read_text(encoding="utf-8")
        self.assertIn("$db.CLIENTE.cpf == $input.cpf", registration)
        self.assertIn("$db.CLIENTE.email == $input.email", registration)
        self.assertIn('status: "ATIVO"', registration)
        self.assertNotIn("dblink", registration)
        self.assertNotIn("password:", registration.split("response =", 1)[1])

        legacy_paths = (
            Path("xano/api/db_xano_bastos/cliente_GET.xs"),
            Path("xano/api/db_xano_bastos/cliente/cliente_id_GET.xs"),
            Path("xano/api/db_xano_bastos/cliente/cliente_id_PATCH.xs"),
            Path("xano/api/db_xano_bastos/cliente/cliente_id_DELETE.xs"),
        )
        for path in legacy_paths:
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn('auth = "CLIENTE"', source)
                self.assertNotIn("util.get_raw_input", source)
                self.assertNotIn("dblink", source)
                self.assertNotIn("password", source.lower())

        profile_patch = legacy_paths[2].read_text(encoding="utf-8")
        self.assertIn("$auth.id == $input.cliente_id", profile_patch)
        self.assertNotIn("cpf?", profile_patch)
        self.assertNotIn("password?", profile_patch)
        customer_delete = legacy_paths[3].read_text(encoding="utf-8")
        self.assertNotIn("db.del CLIENTE", customer_delete)

    def test_address_endpoints_enforce_owner_and_primary_address_rules(self):
        paths = sorted(Path("xano/api/customer").glob("customer_address*.xs"))
        self.assertEqual(len(paths), 5)
        for path in paths:
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn('auth = "CLIENTE"', source)
                self.assertIn("$auth.id", source)
                self.assertNotIn("input.cliente_id", source)

        address_table = Path("xano/table/endereco.xs").read_text(encoding="utf-8")
        self.assertIn('table = "CLIENTE"', address_table)
        self.assertIn('enum status?="ATIVO"', address_table)
        patch = Path(
            "xano/api/customer/customer_address_id_PATCH.xs"
        ).read_text(encoding="utf-8")
        self.assertIn("db.transaction", patch)
        self.assertIn('$input.status == "INATIVO"', patch)
        self.assertIn('value = $updates|set:"principal":false', patch)

        create = Path("xano/api/customer/customer_addresses_POST.xs").read_text(
            encoding="utf-8"
        )
        self.assertIn("db.transaction", create)
        self.assertIn('table = "CLIENTE"', address_table)
        delete = Path(
            "xano/api/customer/customer_address_id_DELETE.xs"
        ).read_text(encoding="utf-8")
        self.assertLess(
            delete.index("$address.cliente_id == $auth.id"),
            delete.index("db.del endereco"),
        )

    def test_customer_ui_uses_state_and_does_not_render_auth_token(self):
        source = Path("voltix/voltix.py").read_text(encoding="utf-8")
        customer_page = source.split("def customer_account_page()", 1)[1].split(
            "\n\napp = rx.App()", 1
        )[0]
        self.assertIn('route="/cliente"', source)
        self.assertIn("State.submit_customer_registration", customer_page)
        self.assertIn("State.submit_customer_login", customer_page)
        self.assertIn("State.save_customer_address", customer_page)
        self.assertNotIn("_customer_auth_token", customer_page)
        self.assertIn("on_load=State.validate_customer_session", source)


if __name__ == "__main__":
    unittest.main()
