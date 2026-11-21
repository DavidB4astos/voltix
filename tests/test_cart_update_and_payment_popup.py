import asyncio
from types import SimpleNamespace
import unittest

import voltix.voltix as app


class CartUpdateAndPaymentPopupTests(unittest.TestCase):
    def test_cart_form_submit_hook_does_not_capture_foreach_item_var(self):
        page = app.customer_cart_page()
        hooks = "\n".join(str(h) for h in page._get_all_hooks())
        self.assertIn("update_cart_item_form", hooks)
        self.assertNotIn("item_rx_state_", [h for h in page._get_all_hooks() if "update_cart_item_form" in str(h)][0])
        self.assertIn('name:"item_id"', str(page))

    def test_update_cart_item_form_delegates_and_validates_item_id(self):
        calls = []

        async def fake_update(item_id, form_data):
            calls.append((item_id, form_data))

        dummy = SimpleNamespace(cart_message="", update_cart_item=fake_update)
        asyncio.run(app.State.update_cart_item_form.fn(dummy, {"item_id": "42", "quantidade": "3"}))
        self.assertEqual(calls, [(42, {"item_id": "42", "quantidade": "3"})])

        asyncio.run(app.State.update_cart_item_form.fn(dummy, {"quantidade": "3"}))
        self.assertEqual(dummy.cart_message, "Item não encontrado no carrinho. Atualize a lista.")

    def test_orders_page_renders_payment_approved_dialog_and_closes_on_false(self):
        rendered = str(app.customer_orders_page())
        self.assertIn("RadixThemesDialog.Root", rendered)
        self.assertIn("Compra aprovada!", rendered)

        closed = []
        dummy = SimpleNamespace(close_payment_approved_modal=lambda: closed.append(True))
        app.State.handle_payment_approved_dialog_open_change.fn(dummy, True)
        self.assertEqual(closed, [])
        app.State.handle_payment_approved_dialog_open_change.fn(dummy, False)
        self.assertEqual(closed, [True])


if __name__ == "__main__":
    unittest.main()
