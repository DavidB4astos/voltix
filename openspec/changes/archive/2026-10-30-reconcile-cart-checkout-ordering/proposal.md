## Why
Snapshot recente confirma ausência de sort nas quatro consultas de item_carrinho das três rotas publicadas, apesar de id asc já previsto localmente. A confirmação compara arrays de revisão por json_encode; uma ordem consistente deve ser explícita. Não foi reproduzida falha de compra e não se afirma que ocorria sempre.
## What Changes
Adicionar somente sort id asc ao GET cart, POST checkout/review e às duas consultas do POST checkout/confirm. Requisitos de ordem compartilhada para apresentação e revisão. Preservar todos os vínculos, filtros, cálculos, autorização e operações existentes.
## Capabilities
### Modified Capabilities
- shopping-cart: itens consultados por ID ascendente.
- checkout-orders: revisão e confirmação usam a mesma ordem de itens por ID.
## Impact
Três endpoints existentes, quatro consultas ordenadas. Sem schema, estoque, pagamento, novas permissões, frontend ou alteração dos writes existentes. A publicação de confirm atualiza seu código, mas não invoca a compra. Sem executar POST de confirmação para teste nesta change.
