from pathlib import Path
import unittest


class InternalSidebarCssTests(unittest.TestCase):
    def test_sidebar_contains_overflow_and_profile_avoids_mid_tld_break(self):
        css = (Path(__file__).resolve().parent.parent / "assets" / "voltix-internal.css").read_text(
            encoding="utf-8"
        )
        self.assertIn(".vx-internal__sidebar{", css)
        self.assertIn("overflow-y:auto", css)
        self.assertIn("minmax(180px,1fr)", css)
        self.assertIn(".vx-profile__value dd{margin:0;font-size:13px;color:#17314b;overflow-wrap:break-word}", css)


if __name__ == "__main__":
    unittest.main()
