## Why

A C3 publicou a consulta e o avanço de status de Pedidos, mas o painel interno ainda não
oferece a tela correspondente. Funcionários e administradores precisam consultar Pedidos e
avançar a etapa operacional sem sair do painel, sem novo backend e sem expor dados
sensíveis. A tela de Atendimentos já validou o padrão de seção, contrato estrito e handlers
server-side que será reutilizado.

## What Changes

- Nova seção **Pedidos** no painel interno, visível a FUNCIONARIO e ADMINISTRADOR ativos.
- Listagem com busca textual (`q` por código ou nome do Cliente), filtro por status,
  paginação de 20, total e ordenação fornecida pelo backend.
- Detalhe com Cliente (nome e e-mail mascarado), itens, endereço de entrega, Pagamento e
  valores persistidos; sem CPF, telefone, senha, hash ou token.
- Controles de avanço de status somente para ADMINISTRADOR, em um passo por vez:
  `PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`; repetição idempotente e
  transições inválidas bloqueadas pela UI e pelo backend.
- Contrato Python estrito próprio, reutilizando helpers de `internal_customers`.
- Três variáveis de ambiente server-side para os endpoints já publicados.
- Nenhuma alteração, publicação ou verificação remota autenticada no Xano.

## Capabilities

### New Capabilities

- `order-panel`: seção desktop de consulta e avanço operacional de Pedidos no painel interno,
  com listagem, detalhe, transições permitidas e estados seguros.

### Modified Capabilities

- `internal-workspace`: a navegação passa a oferecer Clientes, Atendimentos e Pedidos aos
  funcionários, mantendo Produtos, Categorias/marcas e Importação exclusivos de
  administradores.

## Impact

- `voltix/internal_orders.py` (novo contrato), `voltix/voltix.py` (Estado, handlers e UI).
- `assets/voltix-internal.css` (bloco `vx-orders`).
- `.env.example` (três novas variáveis).
- `tests/test_internal_orders.py` e `tests/test_internal_workspace.py`.
- `openspec/specs/order-panel/` e `openspec/specs/internal-workspace/spec.md` após o
  arquivamento.
- Docs de roadmap/handoff.
- Sem mudanças em Xano, tabelas, endpoints, autenticação ou dados.
