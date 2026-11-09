## Why

A C3 entregou consulta e transição de Pedidos, mas o time interno ainda não tem uma visão
consolidada de vendas. A decisão E3 do roadmap exige um dashboard com faturamento e
quantidade de Pedidos (C10), e hoje só é possível somar manualmente a lista de Pedidos.

## What Changes

- Expor **métricas de vendas por período** em um endpoint **somente leitura** no grupo
  existente `Voltix Internal Orders`: `GET reports/sales`.
- Definir o faturamento como a soma de `valor_total` dos Pedidos em
  `PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO` ou `ENTREGUE`, e a quantidade como a
  contagem desses mesmos Pedidos. `AGUARDANDO_PAGAMENTO` e `CANCELADO` ficam fora.
- Período padrão: últimos 30 dias, inclusive hoje, em **UTC**. O cliente pode informar
  `from`/`to` (`YYYY-MM-DD`), com limite de 366 dias.
- Responder com `faturamento`, `pedidos`, `ticket_medio`, `periodo`, `status_incluidos` e
  `serie_diaria` (dias com vendas, em ordem crescente).
- Permitir leitura para `FUNCIONARIO` e `ADMINISTRADOR` ativos; Cliente, visitante e
  interno inativo são negados no backend.
- Não alterar schema, não gravar nada e não expor dados pessoais ou do Cliente.
- **Fora do escopo**: tela no painel, gráficos avançados, exportação, previsões/metas,
  CRM, reembolso e relatórios contábeis.

## Capabilities

### New Capabilities
- `sales-dashboard`: métricas agregadas de vendas por período, com regra de status,
  janela de datas, permissões e resposta sem dados sensíveis.

### Modified Capabilities
- Nenhuma. Consulta e transição de Pedidos continuam regidas por `order-management`
  (C3); cancelamento continua em `order-cancellation` (C2).

## Impact

- **Xano**: um endpoint novo (`reports_sales_GET.xs`) e atualização da descrição do grupo
  `Voltix Internal Orders` para refletir o uso por FUNCIONARIO/ADMINISTRADOR.
- **Frontend**: nenhum.
- **Dados**: leitura de `pedido` (`id`, `data_pedido`, `status`, `valor_total`); nenhuma
  escrita.
- **Publicação**: dry-run + confirmação explícita; verificação remota somente leitura.
