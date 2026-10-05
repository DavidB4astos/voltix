import asyncio
import os
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from urllib.error import HTTPError, URLError

import voltix.voltix as app


class _FakeAdminState:
    _catalog_request = app.State._catalog_request
    _fetch_catalog_entries = app.State._fetch_catalog_entries
    _save_catalog_entry = app.State._save_catalog_entry
    _set_catalog_status = app.State._set_catalog_status

    _auth_token = "runtime-test-token"
    is_authenticated = True
    session_status = "success"
    user_role = "ADMINISTRADOR"
    user_status = "ATIVO"

    categories = []
    categories_loading = False
    categories_message = ""
    category_editing_id = None
    category_form_name = ""
    category_form_description = ""

    brands = []
    brands_loading = False
    brands_message = ""
    brand_editing_id = None
    brand_form_name = ""
    brand_form_description = ""


class _FakeEmployeeState(_FakeAdminState):
    user_role = "FUNCIONARIO"


class CatalogManagementTests(unittest.TestCase):
    def test_catalog_payloads_are_validated(self):
        entry = app._catalog_entry(
            {"id": 1, "name": "GPU", "description": None, "status": "ATIVO"}
        )
        self.assertEqual(entry, app.CatalogEntry(1, "GPU", "", "ATIVO"))
        self.assertEqual(
            app._catalog_entries(
                [{"id": 2, "name": "ASUS", "description": "", "status": "INATIVO"}]
            )[0].id,
            2,
        )

        invalid_records = (
            {"id": True, "name": "X", "status": "ATIVO"},
            {"id": 1, "name": "", "status": "ATIVO"},
            {"id": 1, "name": "X", "status": "UNKNOWN"},
        )
        for record in invalid_records:
            with self.subTest(record=record), self.assertRaises(ValueError):
                app._catalog_entry(record)

        with self.assertRaises(ValueError):
            app._catalog_entries({"id": 1})

    def test_request_helper_accepts_objects_and_lists(self):
        class _Response:
            status = 200

            def __init__(self, body):
                self.body = body

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return self.body

        for body, expected in (
            (b'{"authorized": true}', {"authorized": True}),
            (
                b'[{"id": 1, "name": "GPU", "status": "ATIVO"}]',
                [{"id": 1, "name": "GPU", "status": "ATIVO"}],
            ),
        ):
            with self.subTest(expected=expected), patch(
                "voltix.voltix.urllib.request.urlopen",
                return_value=_Response(body),
            ):
                self.assertEqual(app._request_xano_json("https://example.invalid"), expected)

    def test_xano_routes_authorize_before_catalog_access_and_preserve_uniqueness(self):
        routes = [
            path
            for path in Path("xano/api/catalog_management").rglob("*.xs")
            if path.name != "api_group.xs"
        ]
        self.assertEqual(len(routes), 6)
        for path in routes:
            with self.subTest(path=path):
                source = path.read_text(encoding="utf-8")
                self.assertIn('auth = "user"', source)
                guard = (
                    'precondition ($user.role == "ADMINISTRADOR" '
                    '&& $user.status == "ATIVO")'
                )
                self.assertIn(guard, source)
                guard_position = source.index(guard)
                entity_accesses = [
                    position
                    for position in (
                        source.find("db.query categoria"),
                        source.find("db.get categoria"),
                        source.find("db.add categoria"),
                        source.find("db.patch categoria"),
                        source.find("db.query marca"),
                        source.find("db.get marca"),
                        source.find("db.add marca"),
                        source.find("db.patch marca"),
                    )
                    if position >= 0
                ]
                self.assertTrue(entity_accesses)
                self.assertGreater(min(entity_accesses), guard_position)

        for table_name in ("categoria", "marca"):
            source = Path(f"xano/table/{table_name}.xs").read_text(encoding="utf-8")
            self.assertIn('enum status?="ATIVO"', source)
            self.assertIn('"btree|unique"', source)

    def test_catalog_request_uses_runtime_token_and_rejects_employee(self):
        os.environ[app.XANO_CATEGORIES_URL_ENV] = (
            "https://example.invalid/api:voltix-catalog-management/categories"
        )
        mocked_request = AsyncMock(
            return_value=[
                {"id": 1, "name": "GPU", "description": "", "status": "ATIVO"}
            ]
        )

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                result = await app.State._catalog_request(
                    _FakeAdminState(),
                    app.XANO_CATEGORIES_URL_ENV,
                )
            self.assertEqual(len(result), 1)
            self.assertEqual(
                mocked_request.call_args.kwargs["authorization"],
                "Bearer runtime-test-token",
            )
            self.assertNotIn("runtime-test-token", repr(result))

            mocked_request.reset_mock()
            with self.assertRaises(ValueError):
                await app.State._catalog_request(
                    _FakeEmployeeState(),
                    app.XANO_CATEGORIES_URL_ENV,
                )
            mocked_request.assert_not_called()

        asyncio.run(run())

    def test_missing_catalog_url_fails_explicitly(self):
        with patch.dict(os.environ, {app.XANO_BRANDS_URL_ENV: ""}):
            with self.assertRaisesRegex(ValueError, app.XANO_BRANDS_URL_ENV):
                app._required_environment_url(app.XANO_BRANDS_URL_ENV)

    def test_category_create_and_status_toggle(self):
        record = {"id": 7, "name": "GPU", "description": "Video", "status": "ATIVO"}
        state = _FakeAdminState()
        mocked_request = AsyncMock(side_effect=[record, [record]])
        os.environ[app.XANO_CATEGORIES_URL_ENV] = (
            "https://example.invalid/api:voltix-catalog-management/categories"
        )

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                await app.State.save_category.fn(
                    state,
                    {"name": " GPU ", "description": " Video "},
                )
            self.assertEqual(state.categories_message, "Categoria salva.")
            self.assertEqual(state.categories[0].name, "GPU")
            self.assertEqual(
                mocked_request.call_args_list[0].kwargs["payload"],
                {"name": "GPU", "description": "Video"},
            )

            mocked_request.reset_mock()
            await app.State.save_category.fn(
                state,
                {"name": "  ", "description": ""},
            )
            self.assertEqual(
                state.categories_message,
                "Informe um nome para a categoria.",
            )
            mocked_request.assert_not_called()

            inactive_record = record | {"status": "INATIVO"}
            mocked_request.side_effect = [inactive_record, [inactive_record]]
            state.categories = [app._catalog_entry(record)]
            with patch(
                "voltix.voltix._server_side_xano_request",
                mocked_request,
            ):
                await app.State.toggle_category_status.fn(state, 7)
            self.assertEqual(
                mocked_request.call_args_list[0].kwargs["payload"],
                {"status": "INATIVO"},
            )
            self.assertEqual(state.categories[0].status, "INATIVO")

        asyncio.run(run())

    def test_category_edit_and_reactivation(self):
        os.environ[app.XANO_CATEGORIES_URL_ENV] = (
            "https://example.invalid/api:voltix-catalog-management/categories"
        )
        state = _FakeAdminState()
        state.category_editing_id = 7
        state.categories = [
            app.CatalogEntry(7, "GPU", "Video", "ATIVO")
        ]
        renamed = {"id": 7, "name": "Placas", "description": "Vídeo", "status": "ATIVO"}
        inactive = renamed | {"status": "INATIVO"}
        mocked_request = AsyncMock(
            side_effect=[
                renamed,
                [renamed],
                inactive,
                [inactive],
                renamed,
                [renamed],
            ]
        )

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                await app.State.save_category.fn(
                    state,
                    {"name": "Placas", "description": "Vídeo"},
                )
                await app.State.toggle_category_status.fn(state, 7)
                await app.State.toggle_category_status.fn(state, 7)

            self.assertEqual(
                mocked_request.call_args_list[0].kwargs["method"],
                "PATCH",
            )
            self.assertTrue(
                mocked_request.call_args_list[0].args[0].endswith("/categories/7")
            )
            self.assertEqual(
                mocked_request.call_args_list[2].kwargs["payload"],
                {"status": "INATIVO"},
            )
            self.assertEqual(
                mocked_request.call_args_list[4].kwargs["payload"],
                {"status": "ATIVO"},
            )
            self.assertEqual(state.categories[0].name, "Placas")
            self.assertEqual(state.categories[0].status, "ATIVO")

        asyncio.run(run())

    def test_brand_create_and_safe_http_network_failures(self):
        record = {"id": 3, "name": "ASUS", "description": "", "status": "ATIVO"}
        state = _FakeAdminState()
        mocked_request = AsyncMock(side_effect=[record, [record]])
        os.environ[app.XANO_BRANDS_URL_ENV] = (
            "https://example.invalid/api:voltix-catalog-management/brands"
        )

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                await app.State.save_brand.fn(
                    state,
                    {"name": "ASUS", "description": ""},
                )
            self.assertEqual(state.brands_message, "Marca salva.")
            self.assertEqual(state.brands[0].name, "ASUS")

            forbidden = HTTPError(
                "https://example.invalid",
                403,
                "Forbidden",
                {},
                None,
            )
            mocked_request.side_effect = forbidden
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                with self.assertRaises(HTTPError) as caught:
                    await app.State._catalog_request(
                        state,
                        app.XANO_BRANDS_URL_ENV,
                    )
            self.assertTrue(
                app._catalog_failure_message(caught.exception).startswith("Voc")
            )
            caught.exception.close()

            mocked_request.side_effect = URLError("offline")
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                with self.assertRaises(URLError) as caught:
                    await app.State._catalog_request(
                        state,
                        app.XANO_BRANDS_URL_ENV,
                    )
            self.assertEqual(
                app._catalog_failure_message(caught.exception),
                "Não foi possível concluir a operação. Tente novamente.",
            )

        asyncio.run(run())
