import asyncio
import os
import re
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, patch
from urllib.error import HTTPError

import voltix.voltix as app


class _FakeAdminState:
    _catalog_request = app.State._catalog_request
    _save_product_form = app.State._save_product_form
    _change_product_status = app.State._change_product_status
    _refresh_products = AsyncMock(return_value=True)
    cancel_variation = app.State.cancel_variation.fn
    _form_decimal = staticmethod(app.State._form_decimal)
    _auth_token = "unit-test-placeholder"
    is_authenticated = True
    session_status = "success"
    user_role = "ADMINISTRADOR"
    user_status = "ATIVO"
    products = []
    products_loading = False
    products_message = ""
    product_editing_id = None
    product_form_name = ""
    product_form_description = ""
    product_form_specifications = ""
    product_form_category_id = "3"
    product_form_brand_id = "4"
    variation_form_name = ""
    variation_form_sku = ""
    variation_form_price = ""
    variation_form_quantity = ""
    categories = [app.CatalogEntry(3, "Computadores", "", "ATIVO")]
    brands = [app.CatalogEntry(4, "Voltix", "", "ATIVO")]
    variation_product_id = 1
    variation_editing_id = None


class _FakeEmployeeState(_FakeAdminState):
    user_role = "FUNCIONARIO"


class ProductManagementTests(unittest.TestCase):
    def test_administrative_reads_keep_output_bounded_and_do_not_write(self):
        contracts = [
            ("products", "produto", "nome", {"id", "nome", "descricao", "especificacoes_tecnicas",
                "imagem_principal", "categoria_id", "marca_id", "status", "created_at", "updated_at"}),
            ("variations", "variacao_produto", "sku", {"id", "produto_id", "nome_ou_descricao",
                "sku", "preco", "quantidade_disponivel", "status", "created_at", "updated_at"}),
        ]
        for route, table, sort_field, fields in contracts:
            with self.subTest(route=route):
                source = Path(f"xano/api/product_management/{route}_GET.xs").read_text(encoding="utf-8")
                query = source.split(f"db.query {table}", 1)[1].split(f"as ${route}", 1)[0]
                output = re.search(r"output\s*=\s*\[([^]]*)\]", query, re.S)
                self.assertIsNotNone(output)
                self.assertEqual(set(re.findall(r'"([^"\n]+)"', output.group(1))), fields)
                self.assertRegex(query, rf'sort\s*=\s*\{{\s*{sort_field}:\s*"asc"\s*\}}')
                self.assertNotIn("where", query)  # Maintenance must retain inactive records.
                for write in ["db.add", "db.patch", "db.del", "db.bulk", "db.edit"]:
                    self.assertNotIn(write, source)
                user_lookup = source.split("db.get user", 1)[1].split("as $user", 1)[0]
                user_output = re.search(r"output\s*=\s*\[([^]]*)\]", user_lookup, re.S)
                self.assertIsNotNone(user_output)
                self.assertEqual(set(re.findall(r'"([^"\n]+)"', user_output.group(1))), {"id", "role", "status"})

    def test_product_payloads_include_inactive_existing_relationships_and_decimal_stock(self):
        entries = app._product_entries(
            [
                {
                    "id": 1,
                    "nome": None,
                    "descricao": None,
                    "especificacoes_tecnicas": None,
                    "imagem_principal": None,
                    "categoria_id": 3,
                    "marca_id": 4,
                    "status": "ATIVO",
                }
            ],
            [
                {
                    "id": 5,
                    "produto_id": 1,
                    "nome_ou_descricao": "Padrão",
                    "sku": "VOLTIX-001",
                    "preco": 10.5,
                    "quantidade_disponivel": 0.5,
                    "status": "ATIVO",
                }
            ],
            [app.CatalogEntry(3, "Computadores", "", "INATIVO")],
            [app.CatalogEntry(4, "Voltix", "", "INATIVO")],
        )
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].name, "")
        self.assertEqual(entries[0].category_status, "INATIVO")
        self.assertEqual(entries[0].brand_status, "INATIVO")
        self.assertEqual(entries[0].variations[0].available_quantity, 0.5)

    def test_product_response_rejects_invalid_variation_constraints(self):
        base = {
            "id": 5,
            "produto_id": 1,
            "nome_ou_descricao": "",
            "sku": "SKU-1",
            "preco": 10,
            "quantidade_disponivel": 0,
            "status": "ATIVO",
        }
        for patch_data in (
            {"sku": ""},
            {"preco": 0},
            {"preco": -1},
            {"quantidade_disponivel": -1},
            {"quantidade_disponivel": True},
            {"status": "UNKNOWN"},
        ):
            with self.subTest(patch_data=patch_data), self.assertRaises(ValueError):
                app._product_variation(base | patch_data)

    def test_missing_product_endpoint_configuration_is_explicit(self):
        with patch.dict(os.environ, {app.XANO_PRODUCTS_URL_ENV: ""}):
            with self.assertRaisesRegex(
                ValueError,
                app.XANO_PRODUCTS_URL_ENV,
            ) as caught:
                app._required_environment_url(app.XANO_PRODUCTS_URL_ENV)
        self.assertEqual(
            app._product_failure_message(caught.exception),
            f"Configuração ausente: {app.XANO_PRODUCTS_URL_ENV}.",
        )

    def test_product_request_requires_active_administrator_and_keeps_token_server_side(self):
        os.environ[app.XANO_PRODUCTS_URL_ENV] = (
            "https://example.invalid/api:voltix-product-management/products"
        )
        mocked_request = AsyncMock(return_value=[])

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                await app.State._catalog_request(
                    _FakeAdminState(),
                    app.XANO_PRODUCTS_URL_ENV,
                )
            self.assertTrue(
                mocked_request.call_args.kwargs["authorization"].startswith(
                    "Bearer "
                )
            )
            self.assertIn(
                _FakeAdminState._auth_token,
                mocked_request.call_args.kwargs["authorization"],
            )

            mocked_request.reset_mock()
            with self.assertRaises(ValueError):
                await app.State._catalog_request(
                    _FakeEmployeeState(),
                    app.XANO_PRODUCTS_URL_ENV,
                )
            mocked_request.assert_not_called()

        asyncio.run(run())

    def test_product_create_sends_required_initial_variation(self):
        state = _FakeAdminState()
        state.product_form_name = ""
        mocked_request = AsyncMock(return_value={"id": 9})
        os.environ[app.XANO_PRODUCTS_URL_ENV] = (
            "https://example.invalid/api:voltix-product-management/products"
        )

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                created = await app.State._save_product_form(
                    state,
                    {
                        "variation_name": "Padrão",
                        "variation_sku": " VOLTIX-9 ",
                        "variation_price": "12.50",
                        "variation_quantity": "0.5",
                    },
                )
            self.assertTrue(created)
            self.assertEqual(
                mocked_request.call_args.kwargs["payload"]["variacoes"],
                [
                    {
                        "nome_ou_descricao": "Padrão",
                        "sku": "VOLTIX-9",
                        "preco": 12.5,
                        "quantidade_disponivel": 0.5,
                    }
                ],
            )
            self.assertEqual(
                mocked_request.call_args.kwargs["payload"]["categoria_id"],
                3,
            )

        asyncio.run(run())

    def test_product_form_rejects_invalid_variation_values_before_request(self):
        state = _FakeAdminState()
        mocked_request = AsyncMock(return_value={"id": 9})

        async def run():
            with patch("voltix.voltix._server_side_xano_request", mocked_request):
                with self.assertRaises(ValueError):
                    await app.State._save_product_form(
                        state,
                        {
                            "variation_name": "",
                            "variation_sku": "SKU-1",
                            "variation_price": "0",
                            "variation_quantity": "-1",
                        },
                    )
            mocked_request.assert_not_called()

        asyncio.run(run())

    def test_product_save_http_failure_does_not_report_success(self):
        state = _FakeAdminState()
        state.products = ["last-confirmed-list"]
        failure = HTTPError(
            "https://example.invalid",
            503,
            "Unavailable",
            {},
            None,
        )
        state._catalog_request = AsyncMock(
            side_effect=failure
        )
        state._refresh_products = AsyncMock(return_value=True)
        os.environ[app.XANO_PRODUCTS_URL_ENV] = (
            "https://example.invalid/api:voltix-product-management/products"
        )

        asyncio.run(
            app.State.save_product.fn(
                state,
                {
                    "variation_name": "",
                    "variation_sku": "SKU-1",
                    "variation_price": "1",
                    "variation_quantity": "0",
                },
            )
        )
        self.assertEqual(state.products, ["last-confirmed-list"])
        self.assertNotEqual(state.products_message, "Produto criado.")
        state._refresh_products.assert_not_awaited()
        failure.close()

    def test_product_status_update_uses_patch_and_confirms_reload(self):
        state = _FakeAdminState()
        state._catalog_request = AsyncMock(return_value={"id": 1})
        state._refresh_products = AsyncMock(return_value=True)

        async def run():
            await app.State._change_product_status(state, 1, "INATIVO", "Produto")

        asyncio.run(run())
        state._catalog_request.assert_awaited_once_with(
            app.XANO_PRODUCTS_URL_ENV,
            method="PATCH",
            record_id=1,
            payload={"status": "INATIVO"},
        )

    def test_variation_save_uses_server_side_api_and_refreshes_products(self):
        state = _FakeAdminState()
        state._catalog_request = AsyncMock(return_value={"id": 5})
        state._refresh_products = AsyncMock(return_value=True)
        async def run():
            await app.State.save_variation.fn(
                state,
                {
                    "variation_name": "16 GB",
                    "variation_sku": " SKU-16 ",
                    "variation_price": "1.25",
                    "variation_quantity": "0",
                },
            )

        asyncio.run(run())
        state._catalog_request.assert_awaited_once_with(
            app.XANO_VARIATIONS_URL_ENV,
            method="POST",
            payload={
                "nome_ou_descricao": "16 GB",
                "sku": "SKU-16",
                "preco": 1.25,
                "quantidade_disponivel": 0.0,
                "produto_id": 1,
            },
        )
        state._refresh_products.assert_awaited_once()

    def test_xano_product_endpoints_authorize_before_business_data_access(self):
        endpoint_paths = [
            path
            for path in Path("xano/api/product_management").rglob("*.xs")
            if path.name != "api_group.xs"
        ]
        self.assertEqual(len(endpoint_paths), 7)
        for path in endpoint_paths:
            with self.subTest(path=path):
                source = path.read_text(encoding="utf-8")
                self.assertIn('auth = "user"', source)
                guard = (
                    'precondition ($user.role == "ADMINISTRADOR" '
                    '&& $user.status == "ATIVO")'
                )
                self.assertIn(guard, source)
                guard_position = source.index(guard)
                data_access = [
                    position
                    for position in (
                        source.find("db.query produto"),
                        source.find("db.query variacao_produto"),
                        source.find("db.get produto"),
                        source.find("db.get variacao_produto"),
                        source.find("db.add produto"),
                        source.find("db.add variacao_produto"),
                        source.find("db.patch produto"),
                        source.find("db.patch variacao_produto"),
                        source.find("storage.create_image"),
                    )
                    if position >= 0
                ]
                self.assertTrue(data_access)
                self.assertGreater(min(data_access), guard_position)

    def test_xano_product_tables_hold_domain_fields_and_unique_sku(self):
        product_table = Path("xano/table/produto.xs").read_text(encoding="utf-8")
        variation_table = Path(
            "xano/table/variacao_produto.xs"
        ).read_text(encoding="utf-8")
        self.assertIn("int categoria_id", product_table)
        self.assertIn("int marca_id", product_table)
        self.assertIn('enum status?="ATIVO"', product_table)
        self.assertIn("text imagem_principal?", product_table)
        self.assertIn("text nome_ou_descricao?", variation_table)
        self.assertIn("decimal preco", variation_table)
        self.assertIn("decimal quantidade_disponivel", variation_table)
        self.assertIn('"btree|unique"', variation_table)
        self.assertIn('{name: "sku", op: "asc"}', variation_table)

    def test_xano_creation_and_variation_routes_enforce_domain_constraints(self):
        create_source = Path(
            "xano/api/product_management/products_POST.xs"
        ).read_text(encoding="utf-8")
        add_source = Path(
            "xano/api/product_management/variations_POST.xs"
        ).read_text(encoding="utf-8")
        update_source = Path(
            "xano/api/product_management/variation/variation_id_PATCH.xs"
        ).read_text(encoding="utf-8")
        self.assertIn("At least one product variation is required.", create_source)
        self.assertIn("db.transaction", create_source)
        self.assertIn("$category.status == \"ATIVO\"", create_source)
        self.assertIn("$brand.status == \"ATIVO\"", create_source)
        self.assertIn("$variation.preco > 0", create_source)
        self.assertIn("$variation.quantidade_disponivel >= 0", create_source)
        self.assertIn("return = {type: \"exists\"}", create_source)
        self.assertIn("$input.preco > 0", add_source)
        self.assertIn("$input.quantidade_disponivel >= 0", add_source)
        self.assertIn("$input.preco > 0", update_source)
        self.assertIn("$input.quantidade_disponivel >= 0", update_source)

    def test_image_multipart_keeps_authorization_out_of_request_body(self):
        class _Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return b'{"id": 1}'

        with patch(
            "voltix.voltix.urllib.request.urlopen",
            return_value=_Response(),
        ) as mocked_urlopen:
            response = app._request_xano_multipart(
                "https://example.invalid/api/products/1/image",
                field_name="image_file",
                file_name="front view.png",
                file_data=b"image-content",
                authorization="Bearer unit-test-placeholder",
            )
        self.assertEqual(response, {"id": 1})
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer unit-test-placeholder",
        )
        self.assertIn(b"image-content", request.data)
        self.assertNotIn(b"unit-test-placeholder", request.data)

    def test_product_image_upload_is_mediated_by_state_and_reports_success(self):
        class _FakeUpload:
            name = "main.png"

            async def read(self):
                return b"image-data"

        state = _FakeAdminState()
        state.product_editing_id = 1
        state.product_image_message = ""
        state._refresh_products = AsyncMock(return_value=True)
        os.environ[app.XANO_PRODUCTS_URL_ENV] = (
            "https://example.invalid/api:voltix-product-management/products"
        )
        upload = AsyncMock(return_value={"id": 1})

        async def run():
            with patch(
                "voltix.voltix._server_side_xano_multipart_request",
                upload,
            ):
                await app.State.upload_product_image.fn(state, [_FakeUpload()])

        asyncio.run(run())
        upload.assert_awaited_once()
        self.assertIn("/products/1/image", upload.call_args.args[0])
        self.assertEqual(upload.call_args.kwargs["file_data"], b"image-data")
        self.assertEqual(state.product_image_message, "Imagem principal atualizada.")

    def test_product_image_failure_preserves_confirmed_product_list(self):
        class _FakeUpload:
            name = "main.png"

            async def read(self):
                return b"image-data"

        state = _FakeAdminState()
        state.product_editing_id = 1
        state.products = ["last-confirmed-list"]
        state._refresh_products = AsyncMock(return_value=True)
        os.environ[app.XANO_PRODUCTS_URL_ENV] = (
            "https://example.invalid/api:voltix-product-management/products"
        )
        failure = HTTPError(
            "https://example.invalid",
            503,
            "Unavailable",
            {},
            None,
        )
        upload = AsyncMock(side_effect=failure)

        async def run():
            with patch(
                "voltix.voltix._server_side_xano_multipart_request",
                upload,
            ):
                await app.State.upload_product_image.fn(state, [_FakeUpload()])

        asyncio.run(run())
        self.assertEqual(state.products, ["last-confirmed-list"])
        self.assertNotEqual(state.product_image_message, "Imagem principal atualizada.")
        state._refresh_products.assert_not_awaited()
        failure.close()

    def test_image_endpoint_uses_private_xano_storage(self):
        source = Path(
            "xano/api/product_management/product/product_id_image_POST.xs"
        ).read_text(encoding="utf-8")
        self.assertIn('access = "private"', source)
        self.assertIn("storage.create_image", source)
        self.assertIn("imagem_principal: $stored_image.path", source)
        self.assertNotIn("db.del", source)
        self.assertNotIn("db.bulk.delete", source)

    def test_product_interface_is_admin_only_and_limits_new_associations(self):
        source = Path("voltix/voltix.py").read_text(encoding="utf-8")
        product_form = source.split("    def product_form()", maxsplit=1)[1]
        product_form = product_form.split("    def variation_form()", maxsplit=1)[0]
        product_ui = source.split("    product_management = rx.cond(", maxsplit=1)[1]
        product_ui = product_ui.split("    catalog_management = rx.cond(", maxsplit=1)[0]
        self.assertIn('State.user_role == "ADMINISTRADOR"', product_ui)
        self.assertIn('entry.status == "ATIVO"', product_form)
        self.assertIn("State.product_form_category_id == entry.id.to_string()", product_form)
        self.assertIn("State.product_form_brand_id == entry.id.to_string()", product_form)
        self.assertIn("State.edit_product", product_ui)
        self.assertIn("State.toggle_product_status", product_ui)
        self.assertNotIn("Excluir", product_ui)


if __name__ == "__main__":
    unittest.main()
