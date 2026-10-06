import asyncio
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

import voltix.voltix as app


def _review_response(
    *,
    quantity: int = 2,
    price: float = 12.5,
    stock: float = 3,
    available: bool = True,
) -> dict[str, object]:
    subtotal = quantity * price
    return {
        "endereco_id": 6,
        "endereco": {
            "cep": "01000000",
            "logradouro": "Rua Um",
            "numero": "10",
            "complemento": "",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": "SP",
            "identificacao": "Casa",
        },
        "itens": [
            {
                "item_id": 8,
                "variacao_id": 3,
                "produto_nome": "Teclado",
                "variacao_nome": "ABNT2",
                "sku": "KEY-1",
                "quantidade": quantity,
                "preco_unitario": price,
                "subtotal": subtotal,
                "produto_status": "ATIVO",
                "variacao_status": "ATIVO",
                "estoque_disponivel": stock,
                "disponivel": available,
            }
        ],
        "revisao": [
            {
                "item_id": 8,
                "variacao_id": 3,
                "quantidade": quantity,
                "preco_unitario": price,
                "estoque_disponivel": stock,
                "produto_status": "ATIVO",
                "variacao_status": "ATIVO",
            }
        ],
        "subtotal": subtotal,
        "valor_frete": 0,
        "valor_total": subtotal,
    }


def _order_response(*, detail: bool) -> dict[str, object]:
    result: dict[str, object] = {
        "id": 29,
        "codigo": "VTX-29",
        "data_pedido": "2026-10-06T10:00:00Z",
        "status": "AGUARDANDO_PAGAMENTO",
        "entrega": {
            "cep": "01000000",
            "logradouro": "Rua Um",
            "numero": "10",
            "complemento": "",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": "SP",
            "identificacao": "Casa",
        },
        "itens": [
            {
                "variacao_id": 3,
                "sku": "KEY-1",
                "nome_ou_descricao": "ABNT2",
                "quantidade": 2,
                "preco_unitario": 12.5,
                "subtotal": 25,
            }
        ],
        "subtotal": 25,
        "valor_frete": 0,
        "valor_total": 25,
    }
    if detail:
        result["pagamento"] = {
            "metodo": "PIX",
            "valor": 25,
            "status": "PENDENTE",
        }
    return result


class _CheckoutState:
    _customer_request = app.State._customer_request
    _set_checkout_review = app.State._set_checkout_review
    _set_selected_order = app.State._set_selected_order
    load_customer_orders = app.State.load_customer_orders.fn
    load_customer_order = app.State.load_customer_order.fn
    checkout_address_id = "6"
    _customer_auth_token = "customer-token"
    customer_authenticated = True
    customer_session_status = "success"
    customer_id = 17
    customer_addresses = [
        app.CustomerAddressEntry(
            6,
            17,
            "01000000",
            "Rua Um",
            "10",
            "",
            "Centro",
            "São Paulo",
            "SP",
            "Casa",
            True,
            "ATIVO",
        )
    ]
    _checkout_review = app._checkout_review(_review_response())
    _selected_order = None
    checkout_review_ready = True
    checkout_review_items = _checkout_review.items
    checkout_loading = False
    checkout_message = ""
    checkout_method = "PIX"
    orders = []
    orders_loading = False
    orders_message = ""
    selected_order_items = []
    order_loading = False


class CheckoutOrdersTests(unittest.TestCase):
    def test_checkout_review_parser_checks_totals_stock_and_address_snapshot(self):
        review = app._checkout_review(_review_response())
        self.assertEqual(review.address_id, 6)
        self.assertEqual(review.address.street, "Rua Um")
        self.assertEqual(review.items[0].unit_price, "12.5")
        self.assertEqual(review.subtotal, "25.0")
        self.assertEqual(review.freight, "0")
        self.assertEqual(review.total, "25.0")

        with self.assertRaisesRegex(ValueError, "totals"):
            app._checkout_review(
                {**_review_response(), "valor_total": 24}
            )
        unavailable = _review_response(stock=1, available=False)
        self.assertFalse(app._checkout_review(unavailable).items[0].available)

    def test_order_parser_preserves_historical_prices_delivery_and_pending_payment(self):
        order = app._order_summary(_order_response(detail=True), detail=True)
        self.assertEqual(order.code, "VTX-29")
        self.assertEqual(order.order_items[0].unit_price, "12.5")
        self.assertEqual(order.delivery.street, "Rua Um")
        self.assertEqual(order.payment_status, "PENDENTE")
        self.assertEqual(order.payment_value, "25")

        with self.assertRaisesRegex(ValueError, "payment"):
            invalid = _order_response(detail=True)
            invalid["pagamento"] = {
                "metodo": "PIX",
                "valor": 24,
                "status": "PENDENTE",
            }
            app._order_summary(invalid, detail=True)

    def test_confirmation_requires_own_customer_session_and_valid_review(self):
        state = _CheckoutState()
        state._customer_auth_token = ""
        state.customer_authenticated = False
        state._customer_request = AsyncMock()

        async def run():
            await app.State.confirm_checkout.fn(state, {"metodo_pagamento": "PIX"})
            state._customer_request.assert_not_called()
            self.assertIn("Entre como Cliente", state.checkout_message)

        asyncio.run(run())

    def test_stale_checkout_review_is_replaced_without_creating_order(self):
        state = _CheckoutState()
        current = _review_response(quantity=1, price=15, stock=3)
        current.update({"confirmado": False, "revisao_alterada": True})
        state._customer_request = AsyncMock(return_value=current)

        async def run():
            await app.State.confirm_checkout.fn(state, {"metodo_pagamento": "PIX"})
            request = state._customer_request.call_args
            self.assertEqual(request.args[0], app.XANO_CHECKOUT_CONFIRM_URL_ENV)
            self.assertEqual(request.kwargs["method"], "POST")
            self.assertEqual(request.kwargs["payload"]["endereco_id"], 6)
            self.assertEqual(request.kwargs["payload"]["metodo_pagamento"], "PIX")
            self.assertEqual(state._checkout_review.items[0].quantity, 1)
            self.assertEqual(state._checkout_review.items[0].unit_price, "15")
            self.assertIn("mudaram", state.checkout_message)

        asyncio.run(run())

    def test_unavailable_item_cannot_be_confirmed(self):
        state = _CheckoutState()
        response = _review_response(stock=1, available=False)
        state._checkout_review = app._checkout_review(response)
        state._customer_request = AsyncMock()

        async def run():
            await app.State.confirm_checkout.fn(state, {"metodo_pagamento": "PIX"})
            state._customer_request.assert_not_called()
            self.assertIn("indisponíveis", state.checkout_message)

        asyncio.run(run())

    def test_successful_confirmation_loads_own_order_summary(self):
        state = _CheckoutState()
        confirmation = _review_response()
        confirmation.update(
            {
                "confirmado": True,
                "revisao_alterada": False,
                "pedido_id": 29,
                "codigo": "VTX-29",
            }
        )
        state._customer_request = AsyncMock(
            side_effect=[
                confirmation,
                [_order_response(detail=False)],
                _order_response(detail=True),
            ]
        )

        async def run():
            await app.State.confirm_checkout.fn(
                state,
                {"metodo_pagamento": "PIX"},
            )
            self.assertEqual(state.orders[0].id, 29)
            self.assertEqual(state._selected_order.code, "VTX-29")
            self.assertEqual(state._selected_order.payment_status, "PENDENTE")
            self.assertTrue(state.selected_order_present)
            self.assertEqual(state.selected_order_code, "VTX-29")
            self.assertEqual(state.selected_order_payment_status, "PENDENTE")
            self.assertIsNone(state._checkout_review)
            self.assertEqual(state._customer_request.await_count, 3)

        asyncio.run(run())

    def test_checkout_order_schemas_and_api_contracts_are_customer_scoped(self):
        order_table = Path("xano/table/pedido.xs").read_text(encoding="utf-8")
        item_table = Path("xano/table/item_pedido.xs").read_text(encoding="utf-8")
        payment_table = Path("xano/table/pagamento.xs").read_text(encoding="utf-8")
        self.assertIn('table = "CLIENTE"', order_table)
        self.assertIn('table = "endereco"', order_table)
        self.assertIn('type: "btree|unique"', order_table)
        self.assertIn('type: "btree|unique"', item_table)
        self.assertIn("int quantidade filters=min:1", item_table)
        self.assertIn("decimal preco_unitario", item_table)
        self.assertIn('type: "btree|unique"', payment_table)
        self.assertIn('values = ["PIX", "CARTAO", "BOLETO"]', payment_table)
        self.assertIn('values = ["PENDENTE", "APROVADO", "RECUSADO", "CANCELADO"]', payment_table)

        api_paths = (
            Path("xano/api/customer/checkout_review_POST.xs"),
            Path("xano/api/customer/checkout_confirm_POST.xs"),
            Path("xano/api/customer/orders_GET.xs"),
            Path("xano/api/customer/order_id_GET.xs"),
        )
        for path in api_paths:
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIn('auth = "CLIENTE"', source)
                self.assertIn("$auth.id", source)
                self.assertNotIn("$input.cliente_id", source)

        confirm = api_paths[1].read_text(encoding="utf-8")
        transaction = confirm.split("db.transaction {", 1)[1]
        self.assertIn("as $current_address", transaction)
        self.assertIn("as $current_cart", transaction)
        self.assertIn("as $current_cart_items", transaction)
        self.assertIn("$current_address.cliente_id == $auth.id", transaction)
        self.assertIn("$current_address.status == \"ATIVO\"", transaction)
        self.assertIn("$db.item_carrinho.carrinho_id == $current_cart.id", transaction)
        self.assertIn("$input.revisao|json_encode", confirm)
        self.assertIn("db.transaction", confirm)
        self.assertIn('status: "AGUARDANDO_PAGAMENTO"', confirm)
        self.assertIn('status: "PENDENTE"', confirm)
        self.assertIn('valor_frete: 0', confirm)
        self.assertIn("db.del item_carrinho", confirm)
        self.assertNotIn("db.patch variacao_produto", confirm)
        self.assertNotIn("db.add pedido", transaction.split("else {", 1)[0])

        order_detail = api_paths[3].read_text(encoding="utf-8")
        self.assertIn("$order.cliente_id == $auth.id", order_detail)
        order_list = api_paths[2].read_text(encoding="utf-8")
        self.assertIn("$db.pedido.cliente_id == $auth.id", order_list)

    def test_checkout_and_order_routes_use_state_and_exclude_payment_processing(self):
        source = Path("voltix/voltix.py").read_text(encoding="utf-8")
        checkout_page = source.split("def customer_checkout_page()", 1)[1].split(
            "\ndef customer_orders_page()", 1
        )[0]
        orders_page = source.split("def customer_orders_page()", 1)[1].split(
            "\n\napp = rx.App()", 1
        )[0]
        self.assertIn('route="/checkout"', source)
        self.assertIn('route="/pedidos"', source)
        self.assertIn("State.load_checkout_review", checkout_page)
        self.assertIn("State.confirm_checkout", checkout_page)
        self.assertIn("State.load_customer_order(order.id)", orders_page)
        self.assertIn("State.selected_order_payment_status", orders_page)
        self.assertNotIn("_customer_auth_token", checkout_page)
        self.assertNotIn("_customer_auth_token", orders_page)
        self.assertNotIn("gateway", checkout_page.lower())
        self.assertNotIn("frete real", checkout_page.lower())


if __name__ == "__main__":
    unittest.main()
