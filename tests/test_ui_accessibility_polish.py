import unittest

import voltix.voltix as app


class UiAccessibilityPolishTests(unittest.TestCase):
    def test_public_catalog_select_has_name_and_search_has_id(self):
        rendered = str(app.public_catalog_page())
        self.assertIn("catalog-search", rendered)
        self.assertIn("category_id", rendered)

    def test_auth_and_recovery_pages_declare_autocomplete(self):
        internal_html = str(app.index())
        recovery_html = str(app.internal_recovery_request_page())
        reset_html = str(app.internal_password_reset_page())
        customer_html = str(app.customer_account_page())

        self.assertIn('autoComplete:"email"', internal_html)
        self.assertIn('autoComplete:"current-password"', internal_html)
        self.assertIn('autoComplete:"email"', recovery_html)
        self.assertIn('autoComplete:"one-time-code"', reset_html)
        self.assertIn('autoComplete:"new-password"', reset_html)
        self.assertIn('autoComplete:"name"', customer_html)
        self.assertIn('autoComplete:"tel"', customer_html)

    def test_internal_attendances_empty_state_has_guidance(self):
        rendered = str(app.internal_attendance_panel())
        self.assertIn("registrar o primeiro contato.", rendered)


if __name__ == "__main__":
    unittest.main()
