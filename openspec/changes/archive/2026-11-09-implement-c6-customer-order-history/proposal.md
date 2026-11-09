## Why

A C4 entrega a consulta de Clientes e a C3 entrega a consulta de Pedidos, mas o time
interno ainda não consegue ver, a partir de um Cliente, todos os Pedidos daquele Cliente
em uma única leitura. Hoje é necessário buscar na lista geral de Pedidos e cruzar
manualmente pelo Cliente.

O roadmap (C6) prevê o histórico do Cliente reutilizando as consultas existentes,
mantendo a propriedade do Pedido, a consistência dos valores e o CPF mascarado.

## What Changes

- Expor **histórico de Pedidos por Cliente** em um endpoint **somente leitura** no grupo
  existente `Voltix Internal Customers`: `GET customers/{customer_id}/orders`.
- Responder uma lista paginada, do Pedido mais recente para o mais antigo, com resumo
  (`id`, `codigo`, `data_pedido`, `status`, `subtotal`, `valor_frete`, `valor_total`) e
  **itens inline** (`variacao_id`, `sku`, `nome_ou_descricao`, `quantidade`,
  `preco_unitario`, `subtotal`).
- Permitir filtros opcionais por `status` (seis estados) e por período `from`/`to`
  (`YYYY-MM-DD`, UTC, inclusivo). Sem período padrão: sem filtros, retorna todo o
  histórico paginado.
- Paginação de 20 por padrão, máximo de 50, com totais de itens e páginas.
- Exigir `FUNCIONARIO` ou `ADMINISTRADOR` `ATIVO`; Cliente, visitante e interno inativo
  são negados no backend.
- Validar que o Cliente existe; caso contrário, responder `notfound`.
- **Sem** dados pessoais do Cliente na resposta (apenas `cliente_id`), **sem** métricas
  agregadas de faturamento, **sem** atendimentos, edição de Cliente, exportação ou tela.
- Não alterar schema, C3, C4, C2 ou C10.

## Capabilities

### New Capabilities
- `customer-order-history`: leitura paginada dos Pedidos de um Cliente, com itens,
  filtros por status/período, autorização interna e sem exposição de dados sensíveis.

### Modified Capabilities
- Nenhuma. A consulta de Clientes continua em `internal-customers` (C4) e a consulta de
  Pedidos continua em `order-management` (C3).

## Impact

- **Xano**: um endpoint novo no grupo `Voltix Internal Customers`; nenhuma mudança de
  schema ou de endpoints existentes.
- **Frontend**: nenhum (backend + spec).
- **Dados**: leitura de `pedido`, `item_pedido` e `variacao_produto`; nenhuma escrita.
- **Publicação**: dry-run restrito + confirmação explícita; verificação remota somente
  leitura.
