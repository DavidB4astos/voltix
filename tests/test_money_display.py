import unittest

import voltix.voltix as app


class CartMoneyTextTests(unittest.TestCase):
    def test_two_decimal_amounts(self):
        self.assertEqual(app._cart_money_text("119.90"), "R$ 119,90")
        self.assertEqual(app._cart_money_text("119.50"), "R$ 119,50")

    def test_missing_or_short_fraction_is_padded(self):
        self.assertEqual(app._cart_money_text("119"), "R$ 119,00")
        self.assertEqual(app._cart_money_text("119.5"), "R$ 119,50")
        self.assertEqual(app._cart_money_text("119."), "R$ 119,00")

    def test_zero_and_large_amounts(self):
        self.assertEqual(app._cart_money_text("0.00"), "R$ 0,00")
        self.assertEqual(app._cart_money_text("1234.50"), "R$ 1234,50")

    def test_fraction_is_not_recomputed_for_extra_precision(self):
        self.assertEqual(app._cart_money_text("10.999"), "R$ 10,99")

    def test_invalid_inputs_raise(self):
        for value in ["", "abc", "1a.90", '"119.90"', "119,90", "-119.90", None]:
            with self.assertRaises((ValueError, AttributeError), msg=value):
                app._cart_money_text(value)


if __name__ == "__main__":
    unittest.main()
