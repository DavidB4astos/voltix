## 1. Correção da atualização do carrinho

- [x] 1.1 Adicionar `update_cart_item_form(self, form_data: dict[str, Any])` em `State` e passar `item_id` por input oculto em `_cart_item_view` (`voltix/voltix.py`), removendo `item.id` do `on_submit`

## 2. Pop-up de compra aprovada

- [x] 2.1 Adicionar `payment_approved_modal_open` e handlers de fechamento em `State`, acionando-o em `simulate_order_payment` quando aprovado
- [x] 2.2 Renderizar o modal `Compra aprovada` (`rx.dialog.root`) em `customer_orders_page()` com código do pedido, total e botão de fechar

## 3. Verificação e encerramento

- [x] 3.1 Adicionar testes unitários focados em `tests/` cobrindo `update_cart_item_form` (sem `item_rx_state_` no hook) e o modal de compra aprovada
- [x] 3.2 Executar `python -m unittest discover -s tests -q`, `reflex compile` (restaurando `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`
- [x] 3.3 Registrar evidência em `evidence/verification.md`, arquivar com `openspec archive fix-cart-update-and-payment-popup -y --skip-specs` e solicitar autorização antes de commit/push
