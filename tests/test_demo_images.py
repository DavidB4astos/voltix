import asyncio
import os
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

import voltix.voltix as app
from voltix import demo_images
from voltix.demo_images import DEMO_NAME_TO_SKU, resolve_demo_image, resolve_demo_image_named


class _FakeListState:
    _public_catalog_request = app.State._public_catalog_request
    _fetch_public_products = app.State._fetch_public_products
    _public_product_image = app.State._public_product_image

    public_products = []


class DemoImageNameFallbackTests(unittest.TestCase):
    def test_all_demo_names_map_to_their_sku(self):
        self.assertEqual(len(DEMO_NAME_TO_SKU), 20)
        self.assertEqual(
            DEMO_NAME_TO_SKU["Teclado Logitech K120"], "VTX-DEMO-003"
        )
        self.assertEqual(
            DEMO_NAME_TO_SKU["Mouse Logitech MX Master 3S"], "VTX-DEMO-004"
        )
        self.assertEqual(
            DEMO_NAME_TO_SKU["Processador Intel Core i5-12400F"], "VTX-DEMO-015"
        )

    def test_sku_takes_precedence_over_name(self):
        resolved = resolve_demo_image_named(
            "Teclado Logitech K120",
            "VTX-DEMO-003",
            "https://files.example.invalid/other",
        )
        self.assertEqual(resolved, "/demo/vtx-demo-003.jpg")

    def test_name_fallback_resolves_when_sku_missing(self):
        resolved = resolve_demo_image_named(
            "Mouse Logitech MX Master 3S",
            "",
            "",
        )
        self.assertEqual(resolved, "/demo/vtx-demo-004.jpg")

    def test_name_fallback_resolves_when_sku_is_not_demo(self):
        resolved = resolve_demo_image_named(
            "Processador Intel Core i5-12400F",
            "OUTRO-SKU-1",
            "https://files.example.invalid/signed-image",
        )
        self.assertEqual(resolved, "/demo/vtx-demo-015.jpg")

    def test_pending_demo_name_falls_back_to_existing(self):
        resolved = resolve_demo_image_named(
            "Mouse Logitech G203 LIGHTSYNC",
            "",
            "https://files.example.invalid/signed-image",
        )
        self.assertEqual(resolved, "https://files.example.invalid/signed-image")

    def test_unknown_name_and_sku_is_unchanged(self):
        resolved = resolve_demo_image_named(
            "Produto Generico XYZ",
            "",
            "https://files.example.invalid/signed-image",
        )
        self.assertEqual(resolved, "https://files.example.invalid/signed-image")

    def test_fetch_public_products_resolves_by_name(self):
        state = _FakeListState()
        state._public_catalog_request = AsyncMock(
            return_value=[
                {
                    "id": 7,
                    "nome": "Teclado Logitech K120",
                    "descricao": "Teclado",
                    "especificacoes_tecnicas": "",
                    "categoria_id": 1,
                    "marca_id": 1,
                    "categoria_nome": "Perifericos",
                    "marca_nome": "Logitech",
                    "status": "ATIVO",
                }
            ]
        )
        state._public_product_image = AsyncMock(return_value="")

        products = asyncio.run(app.State._fetch_public_products(state, ""))
        self.assertEqual(
            products[0].image_url,
            "/demo/vtx-demo-003.jpg",
        )


class DemoImageExtensionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        patcher = patch.object(demo_images, "DEMO_ASSETS_DIR", self._tmp.name)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _touch(self, filename):
        with open(os.path.join(self._tmp.name, filename), "wb") as handle:
            handle.write(b"img")

    def test_detects_png(self):
        self._touch("vtx-demo-010.png")
        self.assertEqual(
            resolve_demo_image("VTX-DEMO-010", ""),
            "/demo/vtx-demo-010.png",
        )

    def test_detects_jpg(self):
        self._touch("vtx-demo-010.jpg")
        self.assertEqual(
            resolve_demo_image("VTX-DEMO-010", ""),
            "/demo/vtx-demo-010.jpg",
        )

    def test_detects_jpeg(self):
        self._touch("vtx-demo-010.jpeg")
        self.assertEqual(
            resolve_demo_image("VTX-DEMO-010", ""),
            "/demo/vtx-demo-010.jpeg",
        )

    def test_detects_webp(self):
        self._touch("vtx-demo-010.webp")
        self.assertEqual(
            resolve_demo_image("VTX-DEMO-010", ""),
            "/demo/vtx-demo-010.webp",
        )

    def test_extension_priority_is_png_then_jpg(self):
        self._touch("vtx-demo-010.png")
        self._touch("vtx-demo-010.jpg")
        self.assertEqual(
            resolve_demo_image("VTX-DEMO-010", ""),
            "/demo/vtx-demo-010.png",
        )

    def test_missing_asset_keeps_existing_url(self):
        self.assertEqual(
            resolve_demo_image("VTX-DEMO-010", "https://files.example.invalid/x"),
            "https://files.example.invalid/x",
        )

    def test_non_demo_sku_is_unchanged(self):
        self._touch("vtx-demo-010.png")
        self.assertEqual(
            resolve_demo_image("OUTRO-SKU", "https://files.example.invalid/x"),
            "https://files.example.invalid/x",
        )

    def test_empty_sku_is_unchanged(self):
        self.assertEqual(resolve_demo_image("", ""), "")

