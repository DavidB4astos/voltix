import unittest
from pathlib import Path


def read(relative):
    return Path(relative).read_text(encoding="utf-8")


SOURCE = read("voltix/voltix.py")
CSS = read("assets/voltix-internal.css")


class InternalWorkspaceDesignTests(unittest.TestCase):
    def test_refresh_actions_are_buttons_with_consistent_treatment(self):
        self.assertIn('class_name="vx-customers__refresh"', SOURCE)
        self.assertIn(".vx-customers__refresh{display:inline-flex", CSS)
        self.assertIn("border-radius:8px;background:#fff", CSS)
        self.assertIn("cursor:pointer", CSS)

    def test_redundant_status_pill_was_replaced(self):
        self.assertNotIn('"Acesso interno", class_name="vx-internal__status"', SOURCE)
        self.assertIn('"Sessão ativa", class_name="vx-internal__status"', SOURCE)

    def test_internal_navigation_is_compact_with_clear_selection(self):
        self.assertIn(".vx-internal__nav-item{display:flex;align-items:center;gap:10px", CSS)
        self.assertIn("padding:10px 12px", CSS)
        self.assertIn("is-selected{background:#123c4f;border-color:#2c6479", CSS)

    def test_feedback_panels_are_compact(self):
        self.assertIn(".vx-customers__feedback{display:flex;flex-direction:column;align-items:center;text-align:center;gap:8px;padding:26px 22px", CSS)
        self.assertIn(".vx-orders__empty-detail{display:flex;align-items:center;min-height:96px", CSS)
        self.assertIn(".vx-attendance__empty-detail{display:flex;align-items:center;min-height:96px", CSS)

    def test_tables_have_horizontal_overflow_protection(self):
        for fragment in [
            ".vx-customers__table{overflow-x:auto;max-width:100%}",
            ".vx-crm__table{min-width:640px}",
            ".vx-team__table{min-width:620px}",
            ".vx-history__items{overflow-x:auto;max-width:100%}",
        ]:
            self.assertIn(fragment, CSS)

    def test_internal_tables_remain_readable(self):
        self.assertIn(".vx-internal__content table{font-size:12px}", CSS)


if __name__ == "__main__":
    unittest.main()
