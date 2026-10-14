# 02 — User Stories e Critérios de Aceitação

> Documento da AP2 — Voltix. Entrega: 21/10/2026.
> Fontes: `docs/project-overview.md` (§4/§6), `openspec/specs/`, `openspec/changes/`.
> Formato: `US-xx — Como <papel>, quero <ação>, para <benefício>`, seguido de critérios de aceitação em Dado/Quando/Então **derivados dos cenários já especificados** (cada critério cita a spec de origem). Nenhum comportamento novo é descrito.
> **Atores:** **Cliente**, **Funcionário** e **Administrador** conforme `docs/project-overview.md` §4. O **Visitante** é incluído como público das páginas públicas (§6.1). `US-T1` é um **habilitador técnico**, não uma persona de usuário.

## Legenda de status

- **Implementado** — capability consolidada em `openspec/specs/`.
- **Em andamento** — capability em change ativa (ainda com tarefas pendentes).
- **Pendente** — previsto em documentação, sem spec.

---

## Visitante

> **Visitante** é o ator público das páginas `/` (home) e catálogo, sem sessão autenticada. Não consta como usuário cadastrado em `docs/project-overview.md` §4, mas é o público das capacidades públicas `public-home` e `public-catalog` (`§6.1`).

### US-V1 — Home pública (Implementado)
**Como** visitante, **quero** abrir a página inicial pública, **para** conhecer a Voltix e ser conduzido ao catálogo.

- **Dado** que acesso `/` sem sessão interna, **quando** a home carrega, **então** vejo a vitrine pública (não a tela de login interno). *(origem: `public-home/spec.md` — "Visitor opens the public home")*
- **Dado** que estou na home, **quando** clico em "Explorar produtos", **então** sou levado ao catálogo público existente. *(origem: `public-home/spec.md` — "Visitor interacts with the hero")*
- **Dado** que a home está como esperado, **quando** ela é renderizada, **então** vejo categorias e vitrine de produtos com dados reais do catálogo, sem alterar regras de disponibilidade. *(origem: `public-home/spec.md` — "Visitor views category cards" / "Visitor views the product showcase")*

### US-V2 — Navegar no catálogo público (Implementado)
**Como** visitante, **quero** consultar os produtos ativos, **para** avaliar o que a loja oferece sem precisar de login.

- **Dado** que não possuo sessão, **quando** abro o catálogo, **então** vejo produtos `ATIVO` e não vejo produtos `INATIVO`. *(origem: `public-catalog/spec.md` — "Anonymous visitor lists active products")*
- **Dado** que consulto o catálogo sem credenciais, **quando** envio a requisição, **então** o backend retorna somente dados públicos e não permite criar/editar. *(origem: `public-catalog/spec.md` — "Catalog read endpoint is called without authentication")*

### US-V3 — Filtrar por categoria (Implementado)
**Como** visitante, **quero** selecionar uma categoria ativa, **para** reduzir os produtos exibidos ao meu interesse.

- **Dado** que seleciono uma categoria `ATIVO`, **quando** o filtro é aplicado, **então** vejo somente produtos `ATIVO` daquela categoria. *(origem: `public-catalog/spec.md` — "Visitor filters products by active category")*
- **Dado** que uma categoria está `INATIVO`, **quando** o filtro é montado, **então** ela não aparece como filtro. *(origem: `public-catalog/spec.md` — "Inactive category is not available for navigation")*

### US-V4 — Ver detalhes e variações (Implementado)
**Como** visitante, **quero** abrir os detalhes de um produto, **para** ver preço, disponibilidade e variações ativas.

- **Dado** que abro um produto `ATIVO`, **quando** os detalhes carregam, **então** vejo suas informações e somente variações `ATIVO`, com preço e quantidade disponível. *(origem: `public-catalog/spec.md` — "Visitor opens active product details")*
- **Dado** que uma variação ativa tem estoque zero, **quando** ela é exibida, **então** aparece como indisponível para compra, sem mudar seu status. *(origem: `public-catalog/spec.md` — "Active variation has zero stock")*
- **Dado** que a imagem é privada, **quando** o produto é carregado, **então** recebo uma URL temporária sem o caminho privado original. *(origem: `public-catalog/spec.md` — "Product has a private main image")*

---

## Cliente

### US-C1 — Criar conta (Em andamento)
**Como** cliente, **quero** me cadastrar com meus dados, **para** ter uma conta própria e comprar.

- **Dado** dados válidos (CPF/e-mail únicos, senha), **quando** confirmo o cadastro, **então** minha conta é criada e consigo autenticar. *(origem: `openspec/changes/cadastro-cliente-enderecos/specs/customer-access/spec.md`)*

### US-C2 — Autenticar-me (Em andamento)
**Como** cliente, **quero** fazer login, **para** acessar meus dados, carrinho e pedidos.

- **Dado** que sou cliente `ATIVO` com credenciais válidas, **quando** autentico, **então** obtenho uma sessão de Cliente independente do acesso interno. *(origem: `openspec/changes/cadastro-cliente-enderecos/specs/customer-access/spec.md`)*
- **Dado** que sou cliente `INATIVO`, **quando** tento autenticar, **então** o acesso é bloqueado. *(origem: `openspec/changes/cadastro-cliente-enderecos/specs/customer-access/spec.md`)*

### US-C3 — Consultar e editar meus dados (Em andamento)
**Como** cliente, **quero** ver e atualizar meus dados, **para** mantê-los corretos.

- **Dado** que estou autenticado, **quando** consulto/edito meu perfil, **então** acesso apenas meus próprios dados e não posso alterar CPF livremente. *(origem: `openspec/changes/cadastro-cliente-enderecos/specs/customer-access/spec.md`; `docs/domain-model.md` §4.1)*

### US-C4 — Gerenciar meus endereços (Em andamento)
**Como** cliente, **quero** cadastrar e manter meus endereços, **para** usá-los na entrega.

- **Dado** que estou autenticado, **quando** crio/edito um endereço, **então** ele pertence a mim e pode ser definido como principal (no máximo um principal). *(origem: `openspec/changes/cadastro-cliente-enderecos/specs/customer-addresses/spec.md`; `docs/domain-model.md` §4.2)*
- **Dado** que um endereço foi usado em um Pedido, **quando** tento removê-lo, **então** ele é preservado (não excluído). *(origem: `docs/domain-model.md` §4.2)*

### US-C5 — Manter um carrinho persistente (Implementado)
**Como** cliente, **quero** que meu carrinho seja preservado, **para** continuar a compra depois.

- **Dado** que sou cliente `ATIVO`, **quando** consulto meu carrinho, **então** vejo meus itens e quantidades, podendo estar vazio. *(origem: `shopping-cart/spec.md` — "Customer opens an empty cart" / "Customer returns to a previously used cart")*
- **Dado** que tento acessar o carrinho de outro cliente, **quando** envio a requisição, **então** a operação é rejeitada. *(origem: `shopping-cart/spec.md` — "Customer cannot access another cart")*

### US-C6 — Adicionar, atualizar e remover itens (Implementado)
**Como** cliente, **quero** gerenciar itens do carrinho, **para** ajustar minha compra.

- **Dado** que adiciono uma variação `ATIVO` com estoque, **quando** a operação é aplicada, **então** ela entra no meu carrinho com a quantidade solicitada. *(origem: `shopping-cart/spec.md` — "Customer adds an available active variation")*
- **Dado** que adiciono uma variação já presente, **quando** a operação é aplicada, **então** a quantidade é atualizada, sem duplicar linha. *(origem: `shopping-cart/spec.md` — "Adding an existing variation updates its quantity")*
- **Dado** que informo quantidade fracionária, negativa, zero ou acima do estoque, **quando** a operação é aplicada, **então** ela é tratada conforme a spec (rejeitada ou removendo o item). *(origem: `shopping-cart/spec.md` — "Fractional, negative, or excessive quantity is rejected" / "Zero quantity removes the item")*

### US-C7 — Ver subtotais e total com preço atual (Implementado)
**Como** cliente, **quero** ver os valores calculados com o preço atual, **para** saber quanto pagarei.

- **Dado** que consulto meu carrinho, **quando** o total é calculado, **então** cada item mostra quantidade, preço atual e subtotal, e o total é a soma dos subtotais. *(origem: `shopping-cart/spec.md` — "Customer views cart totals")*
- **Dado** que um preço mudou, **quando** recalculo o carrinho, **então** o próximo cálculo usa o preço atual, sem persistir preço histórico no item. *(origem: `shopping-cart/spec.md` — "Variation price changes while in cart")*

### US-C8 — Confirmar um pedido (checkout) (Em andamento)
**Como** cliente, **quero** revisar meu carrinho e confirmar o pedido, **para** formalizar a compra.

- **Dado** carrinho com itens válidos e endereço próprio ativo, **quando** confirmo, **então** um Pedido é criado com Pagamento `PENDENTE` de valor igual ao total, e o carrinho é esvaziado. *(origem: `openspec/changes/checkout-pedidos/specs/checkout-orders/spec.md`)*
- **Dado** que preço/conteúdo mudou desde a revisão, **quando** tento confirmar, **então** sou obrigado a revisar novamente antes de criar o Pedido. *(origem: `openspec/changes/checkout-pedidos/specs/checkout-orders/spec.md`)*

### US-C9 — Consultar meus pedidos (Em andamento)
**Como** cliente, **quero** ver somente meus pedidos, **para** acompanhar minhas compras.

- **Dado** que estou autenticado, **quando** consulto meus pedidos, **então** acesso apenas meus próprios Pedidos e resumos. *(origem: `openspec/changes/checkout-pedidos/specs/checkout-orders/spec.md`)*

### US-C10 — Simular o pagamento do meu pedido (Implementado)
**Como** cliente, **quero** simular a aprovação do pagamento do meu pedido pendente, **para** concluir a compra no escopo acadêmico.

- **Dado** um Pedido próprio elegível (`PENDENTE` + `AGUARDANDO_PAGAMENTO`), **quando** simulo o pagamento, **então** o Pagamento vira `APROVADO` e o Pedido vira `PAGAMENTO_CONFIRMADO`, sem criar outro Pagamento. *(origem: `order-payment/spec.md` — "Customer simulates payment for an eligible order")*
- **Dado** que tento pagar pedido de outro cliente, **quando** envio a solicitação, **então** a operação é rejeitada sem revelar dados. *(origem: `order-payment/spec.md` — "Customer attempts to pay another customer's order")*

---

## Administrador

### US-A1 — Autenticar-me na área interna (Implementado)
**Como** administrador, **quero** entrar na área interna, **para** gerenciar a operação.

- **Dado** que sou `UsuarioInterno` `ATIVO` com perfil `ADMINISTRADOR`, **quando** autentico em `/interno`, **então** o acesso à área interna é autorizado no backend. *(origem: `internal-access/spec.md` — "Active administrator accesses the protected area")*

### US-A2 — Gerenciar categorias (Implementado)
**Como** administrador, **quero** listar, criar e editar categorias, **para** organizar o catálogo.

- **Dado** que sou administrador autenticado, **quando** crio uma categoria com nome único, **então** ela é criada `ATIVO`. *(origem: `catalog-management/spec.md` — "Administrator creates a category")*
- **Dado** nome ausente ou duplicado, **quando** tento salvar, **então** a operação é rejeitada. *(origem: `catalog-management/spec.md` — "Category name is required" / "Category name must be unique")*

### US-A3 — Gerenciar marcas (Implementado)
**Como** administrador, **quero** listar, criar e editar marcas, **para** associá-las aos produtos.

- **Dado** que sou administrador autenticado, **quando** crio uma marca com nome único, **então** ela é criada `ATIVO`. *(origem: `catalog-management/spec.md` — "Administrator creates a brand")*

### US-A4 — Inativar/reativar sem excluir (Implementado)
**Como** administrador, **quero** inativar e reativar categorias/marcas, **para** preservar histórico.

- **Dado** que altero o status de uma categoria/marca, **quando** salvo, **então** o registro é preservado e exibido no status correspondente; não há exclusão definitiva. *(origem: `catalog-management/spec.md` — "Administrator inactivates a category or brand" / "Category or brand is not permanently deleted")*

### US-A5 — Gerenciar produtos e variações (Em andamento)
**Como** administrador, **quero** cadastrar e manter produtos com ao menos uma variação, **para** comercializá-los.

- **Dado** que sou administrador autenticado, **quando** crio/edito um Produto associado a uma Categoria e Marca, **então** ele possui ao menos uma `VariacaoProduto` com SKU único, preço > 0 e estoque ≥ 0. *(origem: `openspec/changes/gestao-produtos/specs/product-management/spec.md`; `docs/domain-model.md` §3.3/§3.4)*
- **Dado** que inativo/reativo um Produto, **quando** salvo, **então** registros com histórico comercial são preservados (sem exclusão definitiva). *(origem: `openspec/changes/gestao-produtos/specs/product-management/spec.md`)*

---

## Funcionário

### US-F1 — Acessar a área interna (Implementado)
**Como** funcionário, **quero** entrar na área interna, **para** acompanhar a operação conforme minhas permissões.

- **Dado** que sou `UsuarioInterno` `ATIVO` com perfil `FUNCIONARIO`, **quando** autentico, **então** o backend autoriza o acesso à área interna mínima. *(origem: `internal-access/spec.md` — "Active employee accesses the protected area")*
- **Dado** que tento uma operação restrita a administrador (ex.: gerenciar categorias), **quando** envio a requisição, **então** o backend rejeita. *(origem: `catalog-management/spec.md` — "Employee cannot manage categories or brands")*

---

## Funcionalidade pendente (sem user story especificada)

> Itens previstos na documentação, porém **sem comportamento especificado**. Por isso **não** são apresentados como user stories com critérios de aceitação — não há cenário do qual derivá-los, e nenhum critério é inventado.

### F2 — CRM / Atendimento (Pendente)

- **Tratamento:** funcionalidade **pendente**, registrada como lacuna.
- **Origem:** `docs/project-overview.md` §6.3 e `docs/domain-model.md` §6.1 (conceito `Atendimento`).
- **Situação:** sem spec consolidada; **critérios de aceitação não podem ser derivados** do comportamento especificado.
- **Rastreio da pendência:** `03-product-backlog.md` (EP-11).

---

## Habilitador técnico (não é persona de usuário)

### US-T1 — Verificar a integração Reflex↔Xano (Implementado)
**Habilitador técnico** (não representa um ator de negócio): verificar a comunicação com o Xano, **para** garantir a integração técnica da plataforma.

- **Dado** que a verificação é executada com configuração válida, **quando** a chamada é processada, **então** o estado de sucesso com os dados técnicos retornados é exibido. *(origem: `reflex-xano-integration/spec.md` — "Connection check succeeds")*
- **Dado** erro HTTP/rede ou configuração ausente, **quando** a verificação é executada, **então** uma falha explícita é exibida, sem sucesso simulado. *(origem: `reflex-xano-integration/spec.md` — "Connection check fails" / "Backend target is missing")*

---

## Resumo de rastreabilidade

| Faixa | Capability / origem | Status |
|-------|---------------------|--------|
| US-V1 | `public-home` | Implementado |
| US-V2..V4 | `public-catalog` | Implementado |
| US-C1..C3 | `openspec/changes/cadastro-cliente-enderecos/specs/customer-access/spec.md` | Em andamento |
| US-C4 | `openspec/changes/cadastro-cliente-enderecos/specs/customer-addresses/spec.md` | Em andamento |
| US-C5..C7 | `shopping-cart` | Implementado |
| US-C8..C9 | `openspec/changes/checkout-pedidos/specs/checkout-orders/spec.md` | Em andamento |
| US-C10 | `order-payment` | Implementado |
| US-A1, US-F1 | `internal-access` | Implementado |
| US-A2..A4 | `catalog-management` | Implementado |
| US-A5 | `openspec/changes/gestao-produtos/specs/product-management/spec.md` | Em andamento |
| F2 | CRM / Atendimento (pendente, sem user story) | Pendente |
| US-T1 | `reflex-xano-integration` (habilitador técnico) | Implementado |
