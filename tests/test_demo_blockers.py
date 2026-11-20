import unittest
from pathlib import Path

import voltix.voltix as app


SOURCE = Path("voltix/voltix.py").read_text(encoding="utf-8")
RXCONFIG = Path("rxconfig.py").read_text(encoding="utf-8")
ENDPOINT = Path("xano/api/public_catalog/products_GET.xs").read_text(encoding="utf-8")
NAV_CSS = Path("assets/voltix-navigation.css").read_text(encoding="utf-8")
CATALOG_CSS = Path("assets/voltix-catalog-cards.css").read_text(encoding="utf-8")
DETAIL_CSS = Path("assets/voltix-product-details.css").read_text(encoding="utf-8")
INTERNAL_CSS = Path("assets/voltix-internal.css").read_text(encoding="utf-8")


def product_payload(**extra):
    payload = {
        "id": 1,
        "nome": "Produto de teste unitário",
        "descricao": "Descrição",
        "especificacoes_tecnicas": "",
        "categoria_id": 1,
        "marca_id": 1,
        "categoria_nome": "Categoria",
        "marca_nome": "Marca",
        "status": "ATIVO",
        "image_url": "",
    }
    payload.update(extra)
    return payload


class MinimumPriceParsingTests(unittest.TestCase):
    def test_price_is_normalized_with_two_decimal_places(self):
        cases = [
            (119.9, "119.90"),
            ("119.9", "119.90"),
            (119, "119.00"),
            ("119", "119.00"),
            ("0.05", "0.05"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                entry = app._public_product_entry(product_payload(preco_minimo=raw))
                self.assertEqual(entry.min_price, expected)

    def test_absent_or_null_price_is_kept_empty(self):
        for payload in (product_payload(), product_payload(preco_minimo=None),
                        product_payload(preco_minimo="")):
            with self.subTest(payload=payload):
                self.assertEqual(app._public_product_entry(payload).min_price, "")

    def test_invalid_price_is_rejected(self):
        for raw in (True, False, "abc", -1, "NaN", object()):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    app._public_product_entry(product_payload(preco_minimo=raw))

    def test_entry_keeps_default_for_older_callers(self):
        entry = app.PublicProductEntry(
            id=1,
            name="Produto",
            description="",
            technical_specifications="",
            category_name="",
            brand_name="",
            image_url="",
            variations=[],
        )
        self.assertEqual(entry.min_price, "")


class DemoBlockerStaticTests(unittest.TestCase):
    def test_endpoint_exposes_cheapest_active_variation(self):
        self.assertIn("db.query variacao_produto", ENDPOINT)
        self.assertIn('$db.variacao_produto.status == "ATIVO"', ENDPOINT)
        self.assertIn('sort = {preco: "asc"}', ENDPOINT)
        self.assertIn('return = {type: "single"}', ENDPOINT)
        self.assertIn("preco_minimo: $min_price", ENDPOINT)

    def test_card_renders_minimum_price_without_inventing_it(self):
        self.assertIn("min_price: str = \"\"", SOURCE)
        self.assertIn('rx.cond(product.min_price != "",', SOURCE)
        self.assertIn('"a partir de R$ " + product.min_price.replace(".", ",")', SOURCE)
        self.assertIn("vx-catalog-card__price", SOURCE)
        self.assertIn("vx-catalog-card__price", CATALOG_CSS)

    def test_runtime_badge_is_disabled(self):
        self.assertIn("show_built_with_reflex=False", RXCONFIG)

    def test_mobile_header_wraps_without_hidden_destination(self):
        mobile_rule = next(
            line for line in NAV_CSS.splitlines()
            if line.startswith(".vx-nav__mobile-nav{")
        )
        self.assertIn("flex-wrap:wrap", mobile_rule)
        self.assertNotIn("overflow-x:auto", mobile_rule)
        self.assertNotIn("mask-image:linear-gradient", NAV_CSS)

    def test_placeholder_is_shared_and_explicit(self):
        self.assertEqual(SOURCE.count("vx-image-placeholder"), 2)
        self.assertIn("vx-image-placeholder", CATALOG_CSS)
        self.assertIn("vx-image-placeholder", DETAIL_CSS)
        self.assertEqual(SOURCE.count("Imagem não disponível"), 2)
        self.assertNotIn("Foto de outro produto", SOURCE)

    def test_internal_money_cells_do_not_wrap(self):
        self.assertIn('class_name="vx-internal__money-cell"', SOURCE)
        money_rule = next(
            line for line in INTERNAL_CSS.splitlines()
            if ".vx-internal__money-cell{" in line
        )
        self.assertIn("white-space:nowrap", money_rule)
        self.assertIn("font-variant-numeric:tabular-nums", money_rule)


if __name__ == "__main__":
    unittest.main()
