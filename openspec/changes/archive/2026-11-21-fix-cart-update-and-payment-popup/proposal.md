## Why

Foram identificados dois pontos na jornada do Cliente:
1. **Bug na atualização de quantidade do carrinho (`/carrinho`):** `rx.form(..., on_submit=State.update_cart_item(item.id))` dentro de `rx.foreach` gera um `useCallback` (`handleSubmit_*`) no nível da página referenciando `item_rx_state_?.["id"]` fora do escopo do `foreach`, fazendo com que o clique em `Atualizar` não dispare o evento e mantenha quantidade/subtotal/total desatualizados.
2. **Feedback visual de pagamento aprovado (`/pedidos`):** ao aprovar o pagamento simulado, o status atualiza apenas em texto na área do pedido; um pop-up (`rx.dialog`) de **Compra aprovada** deixa a confirmação evidente na demonstração.

## What Changes

- **Correção do formulário de quantidade em `/carrinho` (`voltix/voltix.py`):**
  - Incluir um campo oculto `<input type="hidden" name="item_id" ... />` dentro do formulário de cada item do carrinho e usar `on_submit=State.update_cart_item_form` (sem capturar `item.id` no `useCallback` global), mantendo `update_cart_item(item_id, form_data)` intacto para compatibilidade com testes existentes.
- **Pop-up de compra aprovada em `/pedidos` (`voltix/voltix.py`):**
  - Adicionar estado `payment_approved_modal_open` e handlers de fechamento em `State`.
  - Abrir o modal (`rx.dialog.root`) automaticamente quando `simulate_order_payment` concluir com aprovação (`PAGAMENTO_CONFIRMADO` / `APROVADO`), exibindo código do pedido, total e botão para fechar.
- **Fora do escopo:** alterações em Xano, endpoints, regras de estoque/preço ou specs consolidadas.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- Nenhuma (`skip_specs: true` em `.openspec.yaml`).

## Impact

- **Worktree:** `.worktrees/fix-cart-update-and-payment-popup` (branch `fix-cart-update-and-payment-popup`).
- **Arquivos:** `voltix/voltix.py` e teste focado em `tests/`.
- **Gates:** `python -m unittest discover -s tests -q`, `reflex compile` (com restauração de `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`.
