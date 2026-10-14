# 03 — Product Backlog Consolidado

> Documento da AP2 — Voltix. Entrega: 21/10/2026.
> Fontes: `openspec/specs/`, `openspec/changes/`, `docs/project-overview.md`.
> Consolidação derivada do estado real do repositório. O status reflete a evidência de `openspec list` / `openspec list --specs` no momento da escrita (13/10/2026), não estimativas.

## 1. Convenções

- **Status:**
  - `Implementado` — capability consolidada em `openspec/specs/` (spec do comportamento final).
  - `Em andamento` — capability em change ativa, ainda com tarefas pendentes (mostrado como fração `feitas/total`).
  - `Pendente` — previsto na documentação, sem spec/implementação.
- **Origem:** caminho do artefato que comprova o status.
- **Ordenação:** este backlog lista os épicos por ID; a **ordem de prioridade** está em `04-priorizacao-moscow.md`.

## 2. Status global do repositório

- Specs consolidadas (8): `catalog-management` (5 req), `internal-access` (5), `order-payment` (4), `public-catalog` (5), `public-home` (8), `reflex-xano-integration` (4), `shopping-cart` (5), `visual-interface` (7) — total **43 requisitos**.
- Changes ativas (5, incluindo a change documental `documentacao-ap2`): `checkout-pedidos` (5/9), `cadastro-cliente-enderecos` (11/12), `gestao-produtos` (13/15), `conectar-catalogo-publico-xano` (concluída), `documentacao-ap2` (documental, concluída).
- Changes arquivadas (8): `2026-09-23-integracao-reflex-xano`, `2026-10-07-acesso-interno`, `2026-10-07-carrinho-compras`, `2026-10-07-catalogo-publico`, `2026-10-07-gestao-categorias-marcas`, `2026-10-07-pagamento-pedido`, `2026-10-13-design-interface-voltix`, `2026-10-13-home-publica-voltix`.

## 3. Épicos e itens

### EP-01 — Catálogo público — `Implementado`
**Origem:** `openspec/specs/public-catalog/spec.md`; change arquivada `2026-10-07-catalogo-publico` e change ativa/concluída `conectar-catalogo-publico-xano`.

- BL-01.1 Consulta anônima de produtos `ATIVO` e seus dados gerais.
- BL-01.2 Filtro por categorias `ATIVO`.
- BL-01.3 Detalhes do produto com variações `ATIVO`, preço e estoque.
- BL-01.4 Imagem pública via endpoint dedicado, sem expor caminho privado (change `conectar-catalogo-publico-xano`).
- BL-01.5 Tratamento observável de falhas do catálogo.

### EP-02 — Home pública — `Implementado`
**Origem:** `openspec/specs/public-home/spec.md`; change arquivada `2026-10-13-home-publica-voltix`.

- BL-02.1 Home em `/` com cabeçalho premium.
- BL-02.2 Hero com CTA "Explorar produtos".
- BL-02.3 Faixa de benefícios, cards de categorias e vitrine de produtos com dados reais.
- BL-02.4 Rodapé institucional.
- BL-02.5 Relocação do acesso interno para `/interno` sem mudança de comportamento.

### EP-03 — Interface visual — `Implementado`
**Origem:** `openspec/specs/visual-interface/spec.md`; change arquivada `2026-10-13-design-interface-voltix`.

- BL-03.1 Identidade visual unificada, componentes responsivos e estados de feedback/acessibilidade.

### EP-04 — Acesso interno — `Implementado`
**Origem:** `openspec/specs/internal-access/spec.md`; change arquivada `2026-10-07-acesso-interno`.

- BL-04.1 Login de `UsuarioInterno` provisionado (sem cadastro público).
- BL-04.2 Perfis `FUNCIONARIO`/`ADMINISTRADOR` e status `ATIVO`/`INATIVO`.
- BL-04.3 Autorização de acesso à área protegida no backend.
- BL-04.4 Logout e encerramento de sessão.
- BL-04.5 Separação entre acesso interno e acesso de Cliente.

### EP-05 — Gestão de catálogo (categorias e marcas) — `Implementado`
**Origem:** `openspec/specs/catalog-management/spec.md`; change arquivada `2026-10-07-gestao-categorias-marcas`.

- BL-05.1 CRUD de categorias (nome único, status).
- BL-05.2 CRUD de marcas (nome único, status).
- BL-05.3 Inativação/reativação sem exclusão.
- BL-05.4 Restrição a administradores (backend).
- BL-05.5 Erros de gestão observáveis.

### EP-06 — Gestão de produtos — `Em andamento (13/15)`
**Origem:** `openspec/changes/gestao-produtos` — capability `product-management`.

- BL-06.1 Produto com nome, descrição, especificações, imagem principal opcional, status e auditoria.
- BL-06.2 Associação a exatamente uma Categoria e uma Marca.
- BL-06.3 `VariacaoProduto` mínima (SKU único, preço > 0, estoque ≥ 0, status).
- BL-06.4 Inativação/reativação preservando histórico.
- BL-06.5 Autorização de `ADMINISTRADOR` no backend.

### EP-07 — Acesso e endereços do Cliente — `Em andamento (11/12)`
**Origem:** `openspec/changes/cadastro-cliente-enderecos` — capabilities `customer-access`, `customer-addresses`.

- BL-07.1 Cadastro de Cliente (CPF/e-mail únicos, credenciais protegidas, status).
- BL-07.2 Login e sessão de Cliente independente do interno.
- BL-07.3 Consulta/edição dos próprios dados; bloqueio de inativo.
- BL-07.4 CRUD de Endereco com endereço principal e preservação histórica.

### EP-08 — Carrinho de compras — `Implementado`
**Origem:** `openspec/specs/shopping-cart/spec.md`; change arquivada `2026-10-07-carrinho-compras`.

- BL-08.1 Carrinho persistente por Cliente (isolamento por proprietário).
- BL-08.2 Adicionar/atualizar/remover itens (quantidades inteiras > 0, ≤ estoque).
- BL-08.3 Respeito ao status de produto/variação/estoque atuais.
- BL-08.4 Subtotal/total com preço atual.
- BL-08.5 Interface via State/Python e falhas observáveis.

### EP-09 — Checkout e Pedidos — `Em andamento (5/9)`
**Origem:** `openspec/changes/checkout-pedidos` — capability `checkout-orders`.

- BL-09.1 Revisão do carrinho e seleção de endereço próprio ativo.
- BL-09.2 Revalidação de preço/estoque e nova revisão se houver mudança.
- BL-09.3 Criação atômica de Pedido, ItemPedido e Pagamento `PENDENTE` (frete zero).
- BL-09.4 Esvaziar carrinho após criação; consulta owner-scoped de pedidos.

### EP-10 — Pagamento (simulado) — `Implementado`
**Origem:** `openspec/specs/order-payment/spec.md`; change arquivada `2026-10-07-pagamento-pedido`.

- BL-10.1 Simulação de aprovação do próprio pedido elegível.
- BL-10.2 Preservação do contrato do Pagamento (método/valor, sem parcial).
- BL-10.3 Pagamento não altera inventário.
- BL-10.4 Status confirmado exibido via State.

### EP-11 — CRM / Atendimento — `Pendente`
**Origem:** `docs/project-overview.md` §6.3 e `docs/domain-model.md` §6.1 (conceito `Atendimento`).

- BL-11.1 Consulta de clientes e histórico de compras no CRM.
- BL-11.2 Registro e consulta de atendimentos (assunto, descrição, status, responsável).
- BL-11.3 Associação opcional de atendimento a Pedido do mesmo Cliente.
- **Observação:** não há spec em `openspec/specs/`; portanto os itens não têm comportamento verificável definido.

### EP-12 — Integração Reflex↔Xano (habilitador) — `Implementado`
**Origem:** `openspec/specs/reflex-xano-integration/spec.md`; change arquivada `2026-09-23-integracao-reflex-xano`.

- BL-12.1 Endpoint técnico de saúde/verificação.
- BL-12.2 Verificação pela interface com estados de loading/sucesso/falha.
- BL-12.3 Configuração por ambiente (sem credenciais no código).
- BL-12.4 Escopo de negócio excluído.

## 4. Resumo por status

| Status | Épicos |
|--------|--------|
| Implementado | EP-01, EP-02, EP-03, EP-04, EP-05, EP-08, EP-10, EP-12 |
| Em andamento | EP-06, EP-07, EP-09 |
| Pendente | EP-11 |

## 5. Rastreabilidade item → evidência

| Épico | Evidência principal |
|-------|---------------------|
| EP-01 | `openspec/specs/public-catalog/spec.md` |
| EP-02 | `openspec/specs/public-home/spec.md` |
| EP-03 | `openspec/specs/visual-interface/spec.md` |
| EP-04 | `openspec/specs/internal-access/spec.md` |
| EP-05 | `openspec/specs/catalog-management/spec.md` |
| EP-06 | `openspec/changes/gestao-produtos/proposal.md` |
| EP-07 | `openspec/changes/cadastro-cliente-enderecos/proposal.md` |
| EP-08 | `openspec/specs/shopping-cart/spec.md` |
| EP-09 | `openspec/changes/checkout-pedidos/proposal.md` |
| EP-10 | `openspec/specs/order-payment/spec.md` |
| EP-11 | `docs/project-overview.md` §6.3; `docs/domain-model.md` §6.1 |
| EP-12 | `openspec/specs/reflex-xano-integration/spec.md` |
