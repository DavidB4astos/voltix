## Why
O histórico de pedidos e o resumo selecionado estão empilhados e têm hierarquia visual pouco clara. O cliente precisa distinguir código/data/status, valores históricos, entrega e pagamento sem confundir simulação com cobrança.

## What Changes
- Histórico e resumo em duas colunas desktop, com títulos semânticos, status legíveis e ações específicas por código.
- Valores históricos formatados pelo helper textual existente, sem recalcular ou buscar preço atual.
- Itens e snapshot de entrega legíveis; não inventar nome do produto, rastreamento, prazo ou cancelamento que o modelo não fornece.
- Estados loading/vazio/feedback separados e orientação antes de selecionar um resumo.
- Simulação mantém a condição de pedido AGUARDANDO_PAGAMENTO e pagamento PENDENTE, handler existente e aviso explícito de nenhuma cobrança.

## Capabilities
### Modified Capabilities
- checkout-orders: apresentação desktop do histórico e resumos existentes.

## Impact
Somente UI e CSS escopado; preservar State, handlers, sessão/propriedade, snapshots e regras order-payment. Sem escrita Xano nos testes. Prévia isolada com dados fictícios, sem importar App/State. Mobile apenas empilhamento seguro. Não alterar carrinho, checkout, catálogo, conta, dependências ou lockfiles.
