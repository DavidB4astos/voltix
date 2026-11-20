from types import SimpleNamespace
import unittest

import voltix.voltix as app


class CatalogDetailsModalTests(unittest.TestCase):
    def test_public_catalog_renders_product_details_inside_dialog(self):
        rendered = str(app.public_catalog_page())
        self.assertIn("RadixThemesDialog.Root", rendered)
        self.assertIn("RadixThemesDialog.Content", rendered)
        self.assertIn("product-detail-title", rendered)
        self.assertIn("Fechar detalhes", rendered)

    def test_dialog_open_change_closes_only_when_false(self):
        closed = []
        dummy_state = SimpleNamespace(
            close_public_product_details=lambda: closed.append(True)
        )
        app.State.handle_public_product_dialog_open_change.fn(dummy_state, True)
        self.assertEqual(closed, [])
        app.State.handle_public_product_dialog_open_change.fn(dummy_state, False)
        self.assertEqual(closed, [True])


if __name__ == "__main__":
    unittest.main()
