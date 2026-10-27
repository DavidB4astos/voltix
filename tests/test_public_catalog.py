import asyncio
import io
import time
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.error import HTTPError, URLError

import voltix.voltix as app


class _FakePublicState:
    _public_catalog_request = app.State._public_catalog_request
    _fetch_public_products = app.State._fetch_public_products
    _public_product_image = app.State._public_product_image
    _load_public_catalog_data = app.State._load_public_catalog_data
    load_public_catalog = app.State.load_public_catalog.fn
    load_public_product_details = app.State.load_public_product_details.fn

    public_categories = []
    public_products = []
    public_catalog_loading = False
    public_catalog_loaded = False
    public_catalog_message = ""
    public_category_id = ""
    public_catalog_search = ""
    public_product_loading = False
    public_product_message = ""
    public_product_detail_id = None
    public_selected_product = None


class PublicCatalogTests(unittest.TestCase):
    def setUp(self):
        app._reset_public_catalog_cache()

    def _rate_limit_error(self, retry_after=None):
        headers = {} if retry_after is None else {"Retry-After": retry_after}
        error = HTTPError(
            "https://example.invalid/x",
            429,
            "Too Many Requests",
            headers,
            io.BytesIO(b""),
        )
        self.addCleanup(error.close)
        return error

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
        product = app._public_catalog_products(
            [
                self.product_payload(
                    image_url="https://files.example.invalid/signed-image"
                )
            ]
        )[0]
        self.assertEqual(product.category_name, "Notebooks")
        self.assertEqual(product.brand_name, "Voltix")
        self.assertEqual(
            product.image_url,
            "https://files.example.invalid/signed-image",
        )
        with self.assertRaises(ValueError):
            app._public_catalog_products(
                [self.product_payload(status="INATIVO")]
            )
        with self.assertRaises(ValueError):
            app._public_catalog_products(
                [self.product_payload(imagem_principal="/vault/private.jpg")]
            )
        with self.assertRaises(ValueError):
            app._public_catalog_products(
                [self.product_payload(image_url="http://files.example.invalid/x")]
            )
        with self.assertRaises(ValueError):
            app._public_catalog_products(
                [self.product_payload(image_url=123)]
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
        state._public_product_image.assert_not_awaited()

    def test_invalid_or_expired_image_url_fails_instead_of_rendering(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(
            return_value={"image_url": "http://files.example.invalid/image"}
        )

        async def run():
            with self.assertRaises(ValueError):
                await app.State._public_product_image(state, 7)

        asyncio.run(run())

    def test_public_image_request_uses_dedicated_image_endpoint(self):
        endpoint = "https://example.invalid/api:cVn4Vybh/products"
        request = AsyncMock(return_value={"image_url": None})

        async def run():
            with (
                patch.dict(
                    "os.environ",
                    {app.XANO_PUBLIC_PRODUCT_IMAGE_URL_ENV: endpoint},
                ),
                patch("voltix.voltix._server_side_xano_request", request),
            ):
                result = await app.State._public_product_image(
                    _FakePublicState(), 7
                )
            self.assertEqual(result, "")
            self.assertEqual(
                request.call_args.args[0],
                endpoint + "/7/image",
            )

        asyncio.run(run())

    def test_catalog_loads_public_data_and_signed_images_without_login(self):
        state = _FakePublicState()
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        product = self.product_payload(
            image_url="https://files.example.invalid/signed-image"
        )
        state._public_catalog_request = AsyncMock(
            side_effect=[
                [category],
                [product],
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
        self.assertEqual(state._public_catalog_request.await_count, 2)

    def test_catalog_load_uses_listing_images_without_per_product_requests(self):
        state = _FakePublicState()
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        products = [
            self.product_payload(
                id=7,
                image_url="https://files.example.invalid/image-7",
            ),
            self.product_payload(
                id=8,
                nome="Monitor Voltix",
                image_url="https://files.example.invalid/image-8",
            ),
        ]
        state._public_catalog_request = AsyncMock(
            side_effect=[
                [category],
                products,
            ]
        )
        state._public_product_image = AsyncMock(
            side_effect=AssertionError("per-product image request")
        )

        async def run():
            await app.State.load_public_catalog.fn(state)

        asyncio.run(run())
        self.assertEqual(state._public_catalog_request.await_count, 2)
        state._public_product_image.assert_not_awaited()
        self.assertEqual(
            [product.image_url for product in state.public_products],
            [
                "https://files.example.invalid/image-7",
                "https://files.example.invalid/image-8",
            ],
        )

    def test_catalog_initial_state_is_not_loaded(self):
        state = _FakePublicState()
        self.assertFalse(state.public_catalog_loaded)
        self.assertFalse(state.public_catalog_loading)
        self.assertEqual(state.public_products, [])

    def test_catalog_load_success_marks_state_as_loaded(self):
        state = _FakePublicState()
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        state._public_catalog_request = AsyncMock(
            side_effect=[
                [category],
                [self.product_payload()],
            ]
        )

        async def run():
            await app.State.load_public_catalog.fn(state)

        asyncio.run(run())
        self.assertTrue(state.public_catalog_loaded)
        self.assertFalse(state.public_catalog_loading)
        self.assertEqual(state.public_catalog_message, "")
        self.assertEqual(len(state.public_products), 1)

    def test_catalog_failure_still_marks_state_as_loaded(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(
            side_effect=URLError("backend unavailable")
        )

        async def run():
            await app.State.load_public_catalog.fn(state)

        asyncio.run(run())
        self.assertTrue(state.public_catalog_loaded)
        self.assertFalse(state.public_catalog_loading)
        self.assertNotEqual(state.public_catalog_message, "")
        self.assertEqual(state.public_products, [])

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
        self.assertIn('$category_record.status == "ATIVO"', product_list)
        self.assertIn('$brand_record.status == "ATIVO"', product_list)
        self.assertGreaterEqual(product_list.count('"imagem_principal"'), 2)
        self.assertIn("storage.sign_private_url", product_list)
        self.assertIn("pathname = $product.imagem_principal", product_list)
        self.assertIn("ttl = 3600", product_list)
        self.assertIn("image_url: $image_url", product_list)
        self.assertNotIn("imagem_principal:", product_list)

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
        self.assertIn("on_load=State.enter_public_catalog", source)
        self.assertIn("Indisponível para compra (estoque zero)", catalog_page)
        self.assertIn("Adicionar ao carrinho", catalog_page)
        self.assertIn("State.add_to_cart(variation.id)", catalog_page)
        self.assertNotIn("checkout", catalog_page.lower())


    def test_repeated_navigation_within_ttl_reuses_cached_data(self):
        state = _FakePublicState()
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        product = self.product_payload(
            image_url="https://files.example.invalid/signed-image"
        )
        state._public_catalog_request = AsyncMock(
            side_effect=[
                [category],
                [product],
            ]
        )

        async def run():
            await app.State.load_public_catalog.fn(state)
            await app.State.load_public_catalog.fn(state)

        asyncio.run(run())
        self.assertEqual(state._public_catalog_request.await_count, 2)
        self.assertEqual(
            state.public_products[0].image_url,
            "https://files.example.invalid/signed-image",
        )

    def test_catalog_cache_expires_and_refetches(self):
        state = _FakePublicState()
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        product = self.product_payload()
        state._public_catalog_request = AsyncMock(
            side_effect=[
                [category],
                [product],
                [category],
                [product],
            ]
        )

        async def run():
            await app.State.load_public_catalog.fn(state)
            keys = list(app._public_catalog_cache.keys())
            for key in keys:
                app._public_catalog_cache[key].expires_at = time.monotonic() - 1.0
            await app.State.load_public_catalog.fn(state)

        asyncio.run(run())
        self.assertEqual(state._public_catalog_request.await_count, 4)

    def test_reuse_respects_selected_category(self):
        state = _FakePublicState()
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        state._public_catalog_request = AsyncMock(
            side_effect=[
                [category],
                [self.product_payload(id=7)],
            ]
        )

        async def run():
            await app.State.load_public_catalog.fn(state)
            state.public_category_id = "2"
            state._public_catalog_request = AsyncMock(
                side_effect=[
                    [category],
                    [self.product_payload(id=8)],
                ]
            )
            await app.State.load_public_catalog.fn(state)

        asyncio.run(run())
        self.assertEqual(state._public_catalog_request.await_count, 2)
        self.assertEqual(state.public_products[0].id, 8)

    def test_concurrent_loads_issue_a_single_set_of_requests(self):
        first = _FakePublicState()
        second = _FakePublicState()
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        product = self.product_payload()
        responses = [[category], [product]]
        first._public_catalog_request = AsyncMock(side_effect=responses)
        second._public_catalog_request = AsyncMock(side_effect=responses)

        async def run():
            await asyncio.gather(
                app.State.load_public_catalog.fn(first),
                app.State.load_public_catalog.fn(second),
            )

        asyncio.run(run())
        total = (
            first._public_catalog_request.await_count
            + second._public_catalog_request.await_count
        )
        self.assertEqual(total, 2)
        self.assertEqual(first.public_products[0].id, second.public_products[0].id)

    def test_rate_limit_retry_succeeds_after_transient_429(self):
        error = self._rate_limit_error("20")
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"ok": true}'
        response.__enter__.return_value = response
        response.__exit__.return_value = False

        with (
            patch("urllib.request.urlopen", side_effect=[error, response]),
            patch("time.sleep") as sleep,
        ):
            result = app._request_xano_json("https://example.invalid/x")

        self.assertEqual(result, {"ok": True})
        sleep.assert_called_once_with(20.0)

    def test_persistent_429_is_observable_and_does_not_simulate_success(self):
        error = self._rate_limit_error("20")

        with (
            patch("urllib.request.urlopen", side_effect=[error, error, error]),
            patch("time.sleep"),
            self.assertRaises(HTTPError) as raised,
        ):
            app._request_xano_json("https://example.invalid/x")

        self.assertEqual(raised.exception.code, 429)

    def test_rate_limit_wait_seconds_defaults_and_caps(self):
        without_header = self._rate_limit_error()
        self.assertEqual(
            app._rate_limit_wait_seconds(without_header),
            app.XANO_RATE_LIMIT_DEFAULT_WAIT_SECONDS,
        )
        capped = self._rate_limit_error("999")
        self.assertEqual(
            app._rate_limit_wait_seconds(capped),
            app.XANO_RATE_LIMIT_MAX_WAIT_SECONDS,
        )

    def test_catalog_failure_is_logged_without_sensitive_data(self):
        state = _FakePublicState()
        secret_url = (
            "https://secret.invalid/api:abc/products?token=SEKRET&key=TOP"
        )

        async def run():
            with self.assertLogs("voltix.public_catalog", level="WARNING") as logs:
                with (
                    patch.dict(
                        "os.environ",
                        {app.XANO_PUBLIC_PRODUCTS_URL_ENV: secret_url},
                    ),
                    patch(
                        "voltix.voltix._server_side_xano_request",
                        AsyncMock(side_effect=URLError("backend unavailable")),
                    ),
                ):
                    with self.assertRaises(URLError):
                        await app.State._public_catalog_request(
                            state, app.XANO_PUBLIC_PRODUCTS_URL_ENV
                        )
            return "\n".join(logs.output)

        output = asyncio.run(run())
        self.assertIn("public_catalog.products", output)
        self.assertNotIn("SEKRET", output)
        self.assertNotIn("TOP", output)
        self.assertNotIn("token=", output)
        self.assertNotIn("secret.invalid", output)

    def test_public_search_by_name_sends_q_param(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(
            return_value=[self.product_payload()]
        )

        async def run():
            await app.State._fetch_public_products(state, "", "notebook")

        asyncio.run(run())
        self.assertEqual(
            state._public_catalog_request.call_args.kwargs["query_params"],
            {"q": "notebook"},
        )

    def test_public_search_combined_with_category(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(
            return_value=[self.product_payload()]
        )

        async def run():
            await app.State._fetch_public_products(state, "2", "NOTEBOOK")

        asyncio.run(run())
        self.assertEqual(
            state._public_catalog_request.call_args.kwargs["query_params"],
            {"category_id": "2", "q": "NOTEBOOK"},
        )

    def test_public_search_empty_term_ignored(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(
            return_value=[self.product_payload()]
        )

        async def run():
            await app.State._fetch_public_products(state, "", "   ")

        asyncio.run(run())
        self.assertIsNone(
            state._public_catalog_request.call_args.kwargs["query_params"]
        )

    def test_public_search_case_insensitive_request(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(
            return_value=[self.product_payload(nome="Teclado Voltix")]
        )

        async def run():
            products = await app.State._fetch_public_products(state, "", "TECLADO")

        asyncio.run(run())
        self.assertEqual(
            state._public_catalog_request.call_args.kwargs["query_params"],
            {"q": "TECLADO"},
        )

    def test_public_search_no_results(self):
        state = _FakePublicState()
        state._public_catalog_request = AsyncMock(return_value=[])

        async def run():
            result = await app.State._fetch_public_products(state, "", "inexistente")
            return result

        result = asyncio.run(run())
        self.assertEqual(result, [])

    def test_load_public_catalog_uses_search_state(self):
        state = _FakePublicState()
        state.public_catalog_search = "  mouse  "
        category = {"id": 2, "name": "Notebooks", "description": "", "status": "ATIVO"}
        state._public_catalog_request = AsyncMock(
            side_effect=[
                [category],
                [self.product_payload(nome="Mouse Voltix")],
            ]
        )

        async def run():
            await app.State.load_public_catalog.fn(state)

        asyncio.run(run())
        self.assertEqual(state._public_catalog_request.await_count, 2)
        self.assertEqual(
            state._public_catalog_request.call_args_list[1].kwargs["query_params"],
            {"q": "mouse"},
        )


if __name__ == "__main__":
    unittest.main()
