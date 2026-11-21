## Context

No Reflex, `rx.form(on_submit=State.handler(item.id))` dentro de `rx.foreach` hoistea o `handleSubmit_*` para o componente pai, onde `item_rx_state_` não existe. Passar `item_id` via `<input type="hidden" name="item_id" ... />` elimina a referência fora de escopo e garante que `form_data` chegue completo ao backend Python.

## Goals / Non-Goals

- **Goals:**
  - Fazer o botão `Atualizar` do carrinho atualizar imediatamente a quantidade confirmada, o subtotal do item e o total do carrinho.
  - Exibir pop-up modal `Compra aprovada` quando `simulate_order_payment` confirmar o pagamento.
- **Non-Goals:**
  - Alterar endpoints Xano ou contratos de `shopping-cart` / `order-payment`.

## Decisions

1. **Campo oculto `item_id` + `State.update_cart_item_form`:** mantém `State.update_cart_item(item_id, form_data)` preservado para testes existentes e resolve o hoist do `rx.foreach`.
2. **Modal `rx.dialog.root` em `customer_orders_page`:** controlado por `State.payment_approved_modal_open`, fechando via botão, `Esc` ou clique fora.
