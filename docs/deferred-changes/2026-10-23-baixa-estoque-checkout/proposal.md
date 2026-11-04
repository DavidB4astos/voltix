## Why

O checkout atual valida disponibilidade, cria Pedido/ItemPedido/Pagamento e esvazia o Carrinho, mas não decrementa `quantidade_disponivel`. Assim, uma mesma última unidade pode ser confirmada mais de uma vez.

Esta é a C1 do roadmap. A implementação permanece adiada até que um caminho nativo do Xano prove atomicidade multi-item, rollback conjunto, estoque nunca negativo e preservação do contrato de resposta.

## What Changes

- Caminho candidato: usar `db.increment` para decrementar cada variação com uma condição atômica que exija `id` correspondente, status `ATIVO` e estoque maior ou igual à quantidade pedida.
- Executar todos os decrementos e as gravações de Pedido, ItemPedido, Pagamento e Carrinho na transação existente.
- Se algum decremento retornar zero, abortar a transação e converter somente esse conflito de estoque na resposta atual HTTP 200 com `confirmado=false`.
- Manter o Carrinho sem reserva de estoque e preservar o contrato de confirmação.

O caminho candidato ainda precisa de prova de sintaxe, suporte no runtime atual, participação em `db.transaction`, rollback de todos os itens e comportamento concorrente. Esta proposta não autoriza implementação ou publicação.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `checkout-orders`: quando a change for aprovada e verificada, confirmar pedido e baixa de estoque como uma única operação atômica.

## Impact

- Se retomada, altera somente `xano/api/customer/checkout_confirm_POST.xs` e os testes focados em `tests/test_checkout_orders.py`.
- Não altera tabelas, frontend, endpoints de revisão/carrinho, contratos ou dados reais.
- Requer ambiente Xano isolado, gratuito e autorizado para qualquer prova que escreva dados.
- `db.direct_query` não é requisito do caminho candidato.
- `gestao-produtos` permanece fora do escopo.
