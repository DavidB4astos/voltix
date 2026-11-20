## Context

`selected_product_details()` em `voltix/voltix.py` já recebe `State.public_selected_product` e possui botão `Fechar detalhes` conectado a `State.close_public_product_details`. O problema é apenas de apresentação: ele fica inserido no fluxo normal acima da grade de cards.

## Goals / Non-Goals

- **Goals:**
  - Abrir o detalhe do produto imediatamente visível no centro da tela (modal `rx.dialog`), independentemente da posição de rolagem no catálogo.
  - Permitir fechar via botão `Fechar detalhes`, tecla `Esc` ou clique no backdrop, mantendo a posição de rolagem na grade.
- **Non-Goals:**
  - Criar nova rota de detalhe, alterar endpoints Xano ou modificar regras de estoque/carrinho.

## Decisions

1. **`rx.dialog.root(open=State.public_selected_product != None)`:** envolve o conteúdo existente de `selected_product_details()` em `rx.dialog.content` com largura confortável e `max_height="88vh"` + `overflow_y="auto"`, garantindo que `on_open_change` feche via `State.close_public_product_details` quando `open` for falso.
2. **Preservação de testes e seletores:** manter classes `.vx-product-detail*`, `#product-detail-title`, textos (`DETALHES DO PRODUTO`, `Fechar detalhes`, `Imagem não disponível`, `Variações disponíveis`, `Especificações técnicas`) e handlers existentes.
