import asyncio
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from urllib.error import URLError

import voltix.voltix as app


class _FakePublicState:
    _public_catalog_request = app.State._public_catalog_request
    _fetch_public_products = app.State._fetch_public_products
    _public_product_image = app.State._public_product_image
    load_public_catalog = app.State.load_public_catalog.fn
    load_public_product_details = app.State.load_public_product_details.fn

    public_categories = []
    public_products = []
    public_catalog_loading = False
    public_catalog_message = ""
    public_category_id = ""
    public_product_loading = False
    public_product_message = ""
    public_product_detail_id = None
    public_selected_product = None


class PublicCatalogTests(unittest.TestCase):
    @staticmethod
    def product_payload(**overrides):
        return {
            "id": 7,
            "nome": "Notebook Voltix",
            "descricao": "Computador portátil",
            "especificacoes_tecnicas": "16 GB RAM",
            "categoria_id": 2,
            "marca_id": 3,
            "categoria_nome": "Notebooks",
            "marca_nome": "Voltix",
            "status": "ATIVO",
        } | overrides

    @staticmethod
    def variation_payload(**overrides):
        return {
            "id": 11,
            "produto_id": 7,
            "nome_ou_descricao": "Padrão",
            "sku": "VOL-NB-001",
            "preco": "3299.90",
            "quantidade_disponivel": 0,
            "status": "ATIVO",
        } | overrides

    def test_public_categories_reject_inactive_records(self):
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        self.assertEqual(app._public_catalog_categories([category])[0].name, "Notebooks")
        with self.assertRaises(ValueError):
            app._public_catalog_categories(
                [category | {"status": "INATIVO"}]
            )

    def test_public_product_list_rejects_inactive_and_private_image_fields(self):
        product = app._public_catalog_products([self.product_payload()])[0]
        self.assertEqual(product.category_name, "Notebooks")
        self.assertEqual(product.brand_name, "Voltix")
        self.assertEqual(product.image_url, "")
        with self.assertRaises(ValueError):
            app._public_catalog_products(
                [self.product_payload(status="INATIVO")]
            )
        with self.assertRaises(ValueError):
            app._public_catalog_products(
                [self.product_payload(imagem_principal="/vault/private.jpg")]
            )

    def test_product_details_include_only_active_variations_and_zero_stock(self):
        details = app._public_product_details(
            {
                "product": self.product_payload(),
                "category_name": "Notebooks",
                "brand_name": "Voltix",
                "variations": [self.variation_payload()],
            },
            image_url="https://files.example.invalid/signed-image",
        )
        self.assertEqual(details.image_url, "https://files.example.invalid/signed-image")
        self.assertEqual(details.variations[0].available_quantity, 0)
        self.assertEqual(details.variations[0].status, "ATIVO")
        with self.assertRaises(ValueError):
            app._public_product_details(
                {
                    "product": self.product_payload(),
                    "category_name": None,
                    "brand_name": None,
                    "variations": [
                        self.variation_payload(status="INATIVO")
                    ],
                },
                image_url="",
            )

    def test_public_requests_are_server_side_and_anonymous(self):
        endpoint = "https://example.invalid/api:voltix-public-catalog/products"
        request = AsyncMock(return_value=[])

        async def run():
            with (
                patch.dict(
                    "os.environ",
                    {app.XANO_PUBLIC_PRODUCTS_URL_ENV: endpoint},
                ),
                patch("voltix.voltix._server_side_xano_request", request),
            ):
                await app.State._public_catalog_request(
                    _FakePublicState(),
                    app.XANO_PUBLIC_PRODUCTS_URL_ENV,
                    query_params={"category_id": "2"},
                )
            self.assertEqual(
                request.call_args.args[0],
                endpoint + "?category_id=2",
            )
            self.assertIsNone(request.call_args.kwargs["authorization"])

        asyncio.run(run())

    def test_product_filter_uses_selected_active_category(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(
            return_value=[self.product_payload()]
        )
        state._public_product_image = AsyncMock(return_value="")

        async def run():
            await app.State._fetch_public_products(state, "2")

        asyncio.run(run())
        self.assertEqual(
            state._public_catalog_request.call_args.kwargs["query_params"],
            {"category_id": "2"},
        )

    def test_invalid_or_expired_image_url_fails_instead_of_rendering(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(
            return_value={"image_url": "http://files.example.invalid/image"}
        )

        async def run():
            with self.assertRaises(ValueError):
                await app.State._public_product_image(state, 7)

        asyncio.run(run())

    def test_catalog_loads_public_data_and_signed_images_without_login(self):
        state = _FakePublicState()
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        product = self.product_payload()
        state._public_catalog_request = AsyncMock(
            side_effect=[
                [category],
                [product],
                {"image_url": "https://files.example.invalid/signed-image"},
            ]
        )

        async def run():
            await app.State.load_public_catalog.fn(state)

        asyncio.run(run())
        self.assertFalse(state.public_catalog_loading)
        self.assertEqual(state.public_catalog_message, "")
        self.assertEqual(state.public_categories[0].name, "Notebooks")
        self.assertEqual(
            state.public_products[0].image_url,
            "https://files.example.invalid/signed-image",
        )

    def test_product_detail_load_and_failure_are_observable(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(
            side_effect=[
                {
                    "product": self.product_payload(),
                    "category_name": "Notebooks",
                    "brand_name": "Voltix",
                    "variations": [self.variation_payload()],
                },
                {"image_url": None},
            ]
        )

        async def run_success():
            await app.State.load_public_product_details.fn(state, 7)

        asyncio.run(run_success())
        self.assertIsNotNone(state.public_selected_product)
        self.assertEqual(state.public_selected_product.id, 7)
        self.assertEqual(len(state.public_selected_product.variations), 1)
        self.assertEqual(state.public_product_message, "")

        state.public_selected_product = None
        state._public_catalog_request = AsyncMock(
            side_effect=URLError("backend unavailable")
        )

        async def run_failure():
            await app.State.load_public_product_details.fn(state, 7)

        asyncio.run(run_failure())
        self.assertIsNone(state.public_selected_product)
        self.assertNotEqual(state.public_product_message, "")
        self.assertFalse(state.public_product_loading)

    def test_public_xano_endpoints_are_read_only_and_do_not_expose_private_paths(self):
        root = Path("xano/api/public_catalog")
        endpoint_files = [
            path for path in root.rglob("*.xs") if path.name != "api_group.xs"
        ]
        self.assertEqual(len(endpoint_files), 4)
        for path in endpoint_files:
            source = path.read_text(encoding="utf-8")
            self.assertIn("verb=GET", source)
            self.assertNotIn('auth = "user"', source)
            self.assertNotIn("db.add ", source)
            self.assertNotIn("db.patch ", source)
            self.assertNotIn("db.del ", source)

        product_list = (root / "products_GET.xs").read_text(encoding="utf-8")
        self.assertIn('$db.produto.status == "ATIVO"', product_list)
        self.assertIn('$db.categoria.status == "ATIVO"', product_list)
        self.assertIn('$db.marca.status == "ATIVO"', product_list)
        self.assertNotIn("imagem_principal", product_list)

        details = (root / "product" / "product_id_GET.xs").read_text(
            encoding="utf-8"
        )
        self.assertIn('$product.status == "ATIVO"', details)
        self.assertIn('$db.variacao_produto.status == "ATIVO"', details)
        self.assertNotIn("imagem_principal", details)

        image = (root / "product" / "product_id_image_GET.xs").read_text(
            encoding="utf-8"
        )
        self.assertIn("storage.sign_private_url", image)
        self.assertIn("pathname = $product.imagem_principal", image)
        self.assertIn("ttl = 3600", image)
        self.assertNotIn("response = $product", image)

    def test_public_route_is_anonymous_and_cart_actions_use_customer_state(self):
        source = Path("voltix/voltix.py").read_text(encoding="utf-8")
        catalog_page = source.split("def public_catalog_page()", 1)[1].split(
            "\ndef customer_account_page()", 1
        )[0]
        self.assertIn('route="/catalogo"', source)
        self.assertIn("on_load=State.load_public_catalog", source)
        self.assertIn("Indisponível para compra (estoque zero)", catalog_page)
        self.assertIn("Adicionar ao carrinho", catalog_page)
        self.assertIn("State.add_to_cart(variation.id)", catalog_page)
        self.assertNotIn("checkout", catalog_page.lower())


if __name__ == "__main__":
    unittest.main()
