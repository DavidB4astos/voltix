import time
from types import SimpleNamespace
import unittest

import voltix.voltix as app


class CacheInternalDashboardsTests(unittest.TestCase):
    def test_select_internal_section_skips_reload_within_20s_cache_window(self):
        now = time.monotonic()
        dummy = SimpleNamespace(
            internal_section="clientes",
            user_role="ADMINISTRADOR",
            internal_dashboard=["cached"],
            _internal_dashboard_loaded_at=now,
            internal_crm_loaded=True,
            _internal_crm_loaded_at=now,
            _internal_customer_allowed=lambda: True,
        )
        self.assertIsNone(app.State.select_internal_section.fn(dummy, "dashboard"))
        self.assertEqual(dummy.internal_section, "dashboard")
        self.assertIsNone(app.State.select_internal_section.fn(dummy, "crm"))
        self.assertEqual(dummy.internal_section, "crm")

        dummy._internal_dashboard_loaded_at = now - 25.0
        self.assertEqual(
            app.State.select_internal_section.fn(dummy, "dashboard"),
            app.State.load_internal_dashboard,
        )


if __name__ == "__main__":
    unittest.main()
