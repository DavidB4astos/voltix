import asyncio
import os
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from urllib.error import URLError

import voltix.voltix as app


class _FakeCartState:
    _customer_request = app.State._customer_request
    _load_cart = app.State._load_cart
    _finish_cart_mutation = app.State._finish_cart_mutation

    _customer_auth_token = "customer-cart-token"
    customer_authenticated = True
    customer_session_status = "success"
    customer_id = 31
    cart_id = None
    cart_items = []
    cart_total = "0"
    cart_loading = False
    cart_message = ""


class ShoppingCartTests(unittest.TestCase):
    def test_cart_response_preserves_decimal_values_and_unavailable_items(self):
        snapshot = app._cart_snapshot(
            {
                "carrinho_id": 7,
                "itens": [
                    {
                        "id": 11,
                        "variacao_produto_id": 4,
                        "produto_nome": "Notebook",
                        "produto_status": "ATIVO",
                        "variacao_nome": "16 GB",
                        "variacao_sku": "NOTE-16",
                        "variacao_status": "ATIVO",
                        "quantidade": 2,
                        "preco": 12.35,
                        "quantidade_disponivel": 2,
                        "subtotal": 24.70,
                        "disponivel": True,
                    },
                    {
                        "id": 12,
                        "variacao_produto_id": 5,
                        "produto_nome": "Mouse",
                        "produto_status": "INATIVO",
                        "variacao_nome": "",
                        "variacao_sku": "MOUSE",
                        "variacao_status": "ATIVO",
                        "quantidade": 1,
                        "preco": 3.1,
                        "quantidade_disponivel": 20,
                        "subtotal": 3.1,
                        "disponivel": False,
                    },
                ],
                "total": 27.8,
            }
        )

        self.assertEqual(snapshot.id, 7)
        self.assertEqual(snapshot.items[0].subtotal, "24.7")
        self.assertEqual(snapshot.total, "27.8")
        self.assertTrue(snapshot.items[0].available)
        self.assertFalse(snapshot.items[1].available)

    def test_cart_response_rejects_invalid_quantities_duplicates_and_totals(self):
        valid_item = {
            "id": 11,
            "variacao_produto_id": 4,
            "produto_nome": "Notebook",
            "produto_status": "ATIVO",
            "variacao_nome": "",
            "variacao_sku": "NOTE",
            "variacao_status": "ATIVO",
            "quantidade": 2,
            "preco": 10,
            "quantidade_disponivel": 2,
            "subtotal": 20,
            "disponivel": True,
        }
        with self.assertRaises(ValueError):
            app._cart_snapshot(
                {
                    "carrinho_id": 1,
                    "itens": [{**valid_item, "quantidade": 1.5}],
                    "total": 15,
                }
            )
        with self.assertRaisesRegex(ValueError, "duplicate variation"):
            app._cart_snapshot(
                {
                    "carrinho_id": 1,
                    "itens": [valid_item, {**valid_item, "id": 12}],
                    "total": 40,
                }
            )
        with self.assertRaisesRegex(ValueError, "total"):
            app._cart_snapshot(
                {"carrinho_id": 1, "itens": [valid_item], "total": 19}
            )

    def test_empty_cart_needs_no_persistence_and_has_zero_total(self):
        snapshot = app._cart_snapshot(
            {"carrinho_id": None, "itens": [], "total": 0}
        )
        self.assertIsNone(snapshot.id)
        self.assertEqual(snapshot.items, [])
        self.assertEqual(snapshot.total, "0")

    def test_load_cart_uses_customer_request_and_preserves_confirmed_state_on_error(self):
        state = _FakeCartState()
        prior = app.CartItemEntry(
            11, 4, "Notebook", "", "NOTE", 1, "12.35", "2", "12.35", True
        )
        state.cart_items = [prior]
        state.cart_total = "12.35"
        state._customer_request = AsyncMock(side_effect=URLError("offline"))

        async def run():
            loaded = await app.State._load_cart(state)
            self.assertFalse(loaded)
            self.assertEqual(state.cart_items, [prior])
            self.assertEqual(state.cart_total, "12.35")
            self.assertIn("Não foi possível carregar", state.cart_message)
            state._customer_request.assert_awaited_once_with(app.XANO_CART_URL_ENV)

        asyncio.run(run())

    def test_add_to_cart_uses_customer_state_and_sends_no_owner_or_price(self):
        state = _FakeCartState()
        state._customer_request = AsyncMock(
            return_value={
                "id": 44,
                "carrinho_id": 9,
                "variacao_produto_id": 4,
                "quantidade": 1,
            }
        )
        state._load_cart = AsyncMock(return_value=True)

        async def run():
            await app.State.add_to_cart.fn(state, 4)
            request = state._customer_request.call_args
            self.assertEqual(request.args[0], app.XANO_CART_URL_ENV)
            self.assertEqual(request.kwargs["method"], "POST")
            self.assertEqual(request.kwargs["path"], "items")
            self.assertEqual(
                request.kwargs["payload"],
                {"variacao_id": 4, "quantidade": 1},
            )
            self.assertEqual(
                state.cart_message,
                "Variação adicionada ao carrinho.",
            )

        asyncio.run(run())

    def test_add_to_cart_requires_customer_and_does_not_use_internal_token(self):
        state = _FakeCartState()
        state._customer_auth_token = ""
        state.customer_authenticated = False
        state._customer_request = AsyncMock()

        async def run():
            await app.State.add_to_cart.fn(state, 4)
            state._customer_request.assert_not_called()
            self.assertIn("Entre como Cliente", state.cart_message)

        asyncio.run(run())

    def test_customer_cart_http_request_uses_only_customer_token(self):
        state = _FakeCartState()
        mocked_request = AsyncMock(return_value={"carrinho_id": 9, "itens": [], "total": 0})

        async def run():
            with (
                patch.dict(
                    os.environ,
                    {
                        app.XANO_CART_URL_ENV:
                        "https://example.invalid/api:voltix-customer/cart"
                    },
                ),
                patch("voltix.voltix._server_side_xano_request", mocked_request),
            ):
                await app.State._customer_request(
                    state,
                    app.XANO_CART_URL_ENV,
                    method="PATCH",
                    path="items",
                    record_id=11,
                    payload={"quantidade": 0},
                )

            self.assertEqual(
                mocked_request.call_args.args[0],
                "https://example.invalid/api:voltix-customer/cart/items/11",
            )
            self.assertEqual(
                mocked_request.call_args.kwargs["authorization"],
                "Bearer customer-cart-token",
            )
            self.assertNotIn("internal-runtime-token", str(mocked_request.call_args))

        asyncio.run(run())

    def test_zero_quantity_update_removes_only_the_owned_line(self):
        state = _FakeCartState()
        state.cart_items = [
            app.CartItemEntry(
                11, 4, "Notebook", "", "NOTE", 1, "12.35", "2", "12.35", True
            )
        ]
        state._customer_request = AsyncMock(
            return_value={"id": 11, "removido": True, "quantidade": 0}
        )
        state._load_cart = AsyncMock(return_value=True)

        async def run():
            await app.State.update_cart_item.fn(state, 11, {"quantidade": "0"})
            request = state._customer_request.call_args
            self.assertEqual(request.kwargs["method"], "PATCH")
            self.assertEqual(request.kwargs["path"], "items")
            self.assertEqual(request.kwargs["record_id"], 11)
            self.assertEqual(request.kwargs["payload"], {"quantidade": 0})
            self.assertEqual(state.cart_message, "Item removido do carrinho.")

        asyncio.run(run())

    def test_remove_cart_item_uses_delete_endpoint_for_the_selected_line(self):
        state = _FakeCartState()
        state.cart_items = [
            app.CartItemEntry(
                11, 4, "Notebook", "", "NOTE", 1, "12.35", "2", "12.35", False
            )
        ]
        state._customer_request = AsyncMock(
            return_value={"id": 11, "removido": True}
        )
        state._load_cart = AsyncMock(return_value=True)

        async def run():
            await app.State.remove_cart_item.fn(state, 11)
            request = state._customer_request.call_args
            self.assertEqual(request.kwargs["method"], "DELETE")
            self.assertEqual(request.kwargs["path"], "items")
            self.assertEqual(request.kwargs["record_id"], 11)
            self.assertNotIn("payload", request.kwargs)
            self.assertEqual(state.cart_message, "Item removido do carrinho.")

        asyncio.run(run())

    def test_fractional_quantity_is_rejected_before_request(self):
        state = _FakeCartState()
        state.cart_items = [
            app.CartItemEntry(
                11, 4, "Notebook", "", "NOTE", 1, "12.35", "2", "12.35", True
            )
        ]
        state._customer_request = AsyncMock()

        async def run():
            await app.State.update_cart_item.fn(state, 11, {"quantidade": "1.5"})
            state._customer_request.assert_not_called()
            self.assertIn("inteiro não negativo", state.cart_message)

        asyncio.run(run())

    def test_cart_schema_and_apis_enforce_owner_and_commercial_rules(self):
        cart_table = Path("xano/table/carrinho.xs").read_text(encoding="utf-8")
        item_table = Path("xano/table/item_carrinho.xs").read_text(
            encoding="utf-8"
        )
        self.assertIn('table = "CLIENTE"', cart_table)
        self.assertIn('type: "btree|unique"', cart_table)
        self.assertIn('name: "cliente_id"', cart_table)
        self.assertIn('table = "carrinho"', item_table)
        self.assertIn('table = "variacao_produto"', item_table)
        self.assertIn("int quantidade filters=min:1", item_table)
        self.assertIn('type: "btree|unique"', item_table)
        self.assertIn('name: "carrinho_id"', item_table)
        self.assertIn('name: "variacao_produto_id"', item_table)
        self.assertNotIn("preco", item_table)
        self.assertNotIn("subtotal", item_table)

        endpoints = (
            Path("xano/api/customer/cart_GET.xs"),
            Path("xano/api/customer/cart_items_POST.xs"),
            Path("xano/api/customer/cart_item_id_PATCH.xs"),
            Path("xano/api/customer/cart_item_id_DELETE.xs"),
        )
        for path in endpoints:
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn('auth = "CLIENTE"', source)
                self.assertIn("$auth.id", source)
                self.assertNotIn("$input.cliente_id", source)
                self.assertNotIn("$input.carrinho_id", source)

        read = endpoints[0].read_text(encoding="utf-8")
        self.assertIn("$db.carrinho.cliente_id == $auth.id", read)
        self.assertIn("$cart_item.preco * $cart_item.quantidade", read)
        self.assertIn("$db.variacao_produto.quantidade_disponivel", read)
        self.assertIn("$cart_total + $line_subtotal", read)
        self.assertIn("produto_status", read)
        self.assertIn("variacao_status", read)

        add = endpoints[1].read_text(encoding="utf-8")
        self.assertIn('$variation.status == "ATIVO"', add)
        self.assertIn('$product.status == "ATIVO"', add)
        self.assertIn("$input.quantidade <= $variation.quantidade_disponivel", add)
        self.assertIn("db.transaction", add)
        self.assertIn("db.patch item_carrinho", add)
        self.assertIn("data = {updated_at: now}", add)
        self.assertNotIn("db.patch variacao_produto", add)

        patch = endpoints[2].read_text(encoding="utf-8")
        self.assertIn("$cart.cliente_id == $auth.id", patch)
        self.assertIn("if ($input.quantidade == 0)", patch)
        self.assertIn("db.del item_carrinho", patch)
        self.assertIn('$variation.status == "ATIVO"', patch)
        self.assertIn('$product.status == "ATIVO"', patch)
        self.assertIn("data = {updated_at: now}", patch)

        delete = endpoints[3].read_text(encoding="utf-8")
        self.assertLess(
            delete.index("$cart.cliente_id == $auth.id"),
            delete.index("db.del item_carrinho"),
        )

    def test_catalog_and_customer_cart_pages_use_reflex_state_with_checkout_entry(self):
        source = Path("voltix/voltix.py").read_text(encoding="utf-8")
        catalog_page = source.split("def public_catalog_page()", 1)[1].split(
            "\ndef customer_account_page()", 1
        )[0]
        cart_page = source.split("def customer_cart_page()", 1)[1].split(
            "\ndef customer_checkout_page()", 1
        )[0]
        self.assertIn("State.add_to_cart(variation.id)", catalog_page)
        self.assertIn('route="/carrinho"', source)
        self.assertIn("State.load_cart", cart_page)
        self.assertIn("State.update_cart_item(item.id)", cart_page)
        self.assertIn("State.remove_cart_item(item.id)", cart_page)
        self.assertIn("State.cart_total", cart_page)
        self.assertIn('href="/checkout"', cart_page)
        self.assertNotIn("_customer_auth_token", catalog_page)
        self.assertNotIn("_customer_auth_token", cart_page)
        for out_of_scope in ("pagamento", "pedido", "CRM"):
            self.assertNotIn(out_of_scope, cart_page.lower())


if __name__ == "__main__":
    unittest.main()
