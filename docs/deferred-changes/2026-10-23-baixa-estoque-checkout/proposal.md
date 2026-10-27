## Why

O checkout valida a disponibilidade de estoque na confirmação, mas nunca baixa `quantidade_disponivel` das variações: `checkout_confirm_POST.xs` cria Pedido, ItemPedido e Pagamento e esvazia o Carrinho sem decrementar estoque. Assim, a mesma última unidade pode ser vendida repetidamente e o estoque nunca reflete as vendas.

Esta Change é a C1 do roadmap (`docs/roadmap-changes.md`) e resolve a lacuna crítica registrada: não existe baixa de estoque em nenhum ponto do backend Xano.

## What Changes

- Baixar atomicamente `quantidade_disponivel` de cada VariaçãoProduto do Carrinho na confirmação válida do Pedido, dentro da transação já existente do checkout.
- Validar disponibilidade com leitura travada da variação (lock de linha) e aplicar a baixa por meio de `UPDATE` guardado (`quantidade_disponivel >= quantidade`), impedindo estoque negativo e compras concorrentes da última unidade.
- Manter o contrato de resposta atual: estoque insuficiente continua retornando HTTP 200 com `confirmado=false`, sem criar Pedido, ItemPedido ou Pagamento e sem alterar estoque.
- Preservar o Carrinho sem reserva de estoque, a criação de Pedido/itens/Pagamento, a limpeza do Carrinho e `valor_frete: 0`.
- Reutilizar `checkout_confirm_POST.xs` e os padrões de transação/erro existentes; nenhuma nova tabela ou entidade.

Ficam fora desta Change: cancelamento e devolução de estoque, reserva de estoque, entidade ou tabela de movimentação de estoque, painel de pedidos, dashboard de vendas, frete, aprovação/simulação de pagamento e qualquer alteração de frontend.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `checkout-orders`: a confirmação passa a baixar estoque atomicamente, com garantia de estoque não negativo e serialização da disputa pela última unidade, mantendo o contrato de resposta e o comportamento de indisponibilidade atuais.

## Impact

- Altera `xano/api/customer/checkout_confirm_POST.xs` (baixa transacional via `db.direct_query`); nenhum outro endpoint é alterado.
- Atualiza `tests/test_checkout_orders.py` (a suíte atual afirmava que o checkout não altera estoque).
- Não altera `voltix/voltix.py`, o frontend, as tabelas do Xano nem o contrato de resposta.
- Depende de confirmação técnica obrigatória: `db.direct_query` deve participar da mesma transação e do rollback do checkout (ver `design.md` e tarefa 1).
- `gestao-produtos` permanece ativa com **13/15** tarefas e pendências de validação (5.2/5.3) documentadas e versionadas; não é alterada por esta Change.
