import unittest
from pathlib import Path


def read(relative):
    return Path(relative).read_text(encoding="utf-8")


SOURCE = read("voltix/voltix.py")
NAV_CSS = read("assets/voltix-navigation.css")
HOME_CSS = read("assets/voltix-home.css")
CATALOG_CSS = read("assets/voltix-catalog-cards.css")


class StorefrontHeaderTests(unittest.TestCase):
    def test_mobile_header_is_rendered_for_public_pages(self):
        self.assertIn('class_name="vx-nav__mobile"', SOURCE)
        self.assertIn('"vx-nav__pill"', SOURCE)
        self.assertIn('class_name="vx-nav__mobile-nav"', SOURCE)
        self.assertIn('aria_label="Navegação principal"', SOURCE)

    def test_desktop_header_destinations_are_preserved(self):
        for fragment in [
            'desktop_link("Início", "/")',
            'desktop_link("Produtos", "/catalogo")',
            'desktop_link("Minha conta", "/cliente", icon="user")',
            'desktop_link("Carrinho", "/carrinho", icon="shopping-cart")',
        ]:
            self.assertIn(fragment, SOURCE)

    def test_active_route_marks_aria_current_in_header(self):
        self.assertIn('aria_current="page" if is_active else None', SOURCE)

    def test_legacy_header_is_not_rendered_anymore(self):
        self.assertNotIn("legacy_header", SOURCE)
        self.assertNotIn("vx-nav__legacy", SOURCE)
        self.assertNotIn("vx-nav__legacy", NAV_CSS)

    def test_mobile_header_css_is_compact_and_scoped(self):
        self.assertIn(".vx-nav__mobile{display:none}", NAV_CSS)
        self.assertIn("@media(max-width:1023px)", NAV_CSS)
        self.assertIn(".vx-nav__pill.is-active", NAV_CSS)
        self.assertIn("scroll-snap-type:x proximity", NAV_CSS)
        self.assertIn(".vx-nav__mobile-nav::-webkit-scrollbar{display:none}", NAV_CSS)


class HomeCategoryBarTests(unittest.TestCase):
    def test_category_scroll_is_keyboard_reachable_and_snaps(self):
        self.assertIn('class_name="vx-home-category-scroll"', SOURCE)
        self.assertIn('class_name="vx-home-category-link"', SOURCE)
        self.assertIn("scroll-snap-type:x proximity", HOME_CSS)
        self.assertIn("overscroll-behavior-x:contain", HOME_CSS)

    def test_category_bar_has_a_scroll_affordance(self):
        self.assertIn("mask-image:linear-gradient", HOME_CSS)


class CatalogGridTests(unittest.TestCase):
    def test_catalog_grid_uses_stable_breakpoint_faixas(self):
        self.assertIn('class_name="vx-catalog-grid"', SOURCE)
        self.assertIn("@media(min-width:768px){.vx-catalog-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}", CATALOG_CSS)
        self.assertIn("@media(min-width:1280px){.vx-catalog-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}", CATALOG_CSS)
        self.assertIn("grid-template-columns:minmax(0,1fr);gap:1.5rem", CATALOG_CSS)

    def test_card_media_keeps_a_stable_aspect_ratio(self):
        self.assertIn("aspect-ratio:4/3", CATALOG_CSS)


class CatalogCreditsTests(unittest.TestCase):
    def test_credit_links_and_notice_are_preserved(self):
        self.assertIn('class_name="vx-catalog-card__credit"', SOURCE)
        self.assertIn('"Fonte"', SOURCE)
        self.assertIn("vx-catalog-card__credit-notice", SOURCE)

    def test_credit_text_is_compact(self):
        self.assertIn(".vx-catalog-card__credit{font-size:.68rem", CATALOG_CSS)
        self.assertIn(".vx-catalog-card__credit-notice{font-size:.64rem", CATALOG_CSS)


if __name__ == "__main__":
    unittest.main()
