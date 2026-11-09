## Why

Depois que o pagamento é confirmado, o Pedido fica parado em `PAGAMENTO_CONFIRMADO`: não há
consulta interna de pedidos nem forma de avançar para `EM_PREPARACAO`, `ENVIADO` e
`ENTREGUE`. O time interno não consegue operar a expedição pelo sistema, e o cancelamento
da C2 só cobre `AGUARDANDO_PAGAMENTO` e `PAGAMENTO_CONFIRMADO`.

## What Changes

- Expor **consulta interna de pedidos**: lista paginada com filtros (`status`, busca por
  código ou nome do Cliente) e detalhe completo (Cliente, itens, endereço de entrega e
  Pagamento), acessível a `FUNCIONARIO` e `ADMINISTRADOR` ativos.
- Expor **avanço de status** apenas para `ADMINISTRADOR` ativo, em sequência estrita:
  `PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`.
- Reutilizar o cancelamento da C2 (`order-cancellation`), sem duplicar regra nem permitir
  transição a partir de `CANCELADO` ou `ENTREGUE`.
- Não expor dados sensíveis do Cliente (CPF, telefone, senha): apenas nome, e-mail
  mascarado no detalhe, além do endereço de entrega necessário à operação.
- Nenhuma alteração de schema, nenhuma tela nova e nenhuma dependência externa.

## Capabilities

### New Capabilities
- `order-management`: consulta interna de Pedidos e transições operacionais de status com
  permissões e sequência validadas no backend.

### Modified Capabilities
- Nenhuma. O cancelamento continua regido por `order-cancellation` (C2).

## Impact

- **Xano**: três endpoints no grupo existente `Voltix Internal Orders`:
  `GET orders`, `GET orders/{order_id}` e `POST orders/{order_id}/status`.
- **Frontend**: nenhum (painel de pedidos fica para change própria).
- **Dados**: sem migração; leitura de `pedido`, `item_pedido`, `variacao_produto`,
  `pagamento` e `CLIENTE`; escrita apenas em `pedido.status`.
- **Publicação**: dry-run + confirmação explícita; verificação remota somente leitura por
  padrão.
- **Fora do escopo**: transportadora/rastreio, CRM, métricas/dashboard (C10), tela no
  painel, edição de itens ou valores, reembolso.
