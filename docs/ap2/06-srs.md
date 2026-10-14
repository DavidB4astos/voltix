# 06 — SRS (Software Requirements Specification)

> Documento da AP2 — Voltix. Entrega: 21/10/2026.
> Fontes: `openspec/specs/` (43 requisitos), `openspec/changes/`, `docs/project-overview.md`, `docs/domain-model.md`, `AGENTS.md`.
> Este SRS **consolida e referencia** o comportamento já especificado. Para detalhe e critérios de aceitação, consultar a spec de origem (evita duplicação). Requisitos ainda não especificados são marcados como **pendente** ou **a definir**.

## 1. Introdução

### 1.1 Propósito
Especificar os requisitos funcionais, não funcionais e casos de uso do sistema Voltix, consolidando a documentação existente.

### 1.2 Escopo
Plataforma de e-commerce de tecnologia com CRM integrado, composta por loja pública, área de cliente, área interna e CRM. Ver `docs/project-overview.md` §5.

### 1.3 Definições
- **RF** — requisito funcional; **RNF** — requisito não funcional; **UC** — caso de uso.
- **Capability** — unidade de comportamento especificada no OpenSpec.
- **Spec consolidada** — comportamento implementado em `openspec/specs/`.
- Atores: **Visitante** (público das páginas públicas, sem sessão — `docs/project-overview.md` §6.1), **Cliente**, **Funcionário**, **Administrador**.
- Termos de domínio em `docs/domain-model.md`.

### 1.4 Referências
`docs/project-overview.md`, `docs/domain-model.md`, `AGENTS.md`, `openspec/specs/*`, `openspec/changes/*`.

## 2. Requisitos Funcionais (RF)

> **Nota de escopo:** os RF abaixo são **enunciados resumidos** que referenciam a **spec consolidada de origem**; o texto normativo completo e os critérios de aceitação permanecem na spec (decisão deliberada de não duplicar). Requisitos sem spec são marcados como **pendente**.

### 2.1 Integração Reflex↔Xano — `reflex-xano-integration/spec.md` (Implementado)
| ID | Requisito |
|----|-----------|
| RF-XANO-01 | O backend disponibiliza um endpoint técnico de disponibilidade, sem entidades de negócio. |
| RF-XANO-02 | O frontend executa a verificação e representa loading/sucesso/falha. |
| RF-XANO-03 | A URL do backend é configurável por ambiente, sem credenciais no código. |
| RF-XANO-04 | A validação é independente de autenticação, catálogo, carrinho, pedidos e CRM. |

### 2.2 Home pública — `public-home/spec.md` (Implementado)
| ID | Requisito |
|----|-----------|
| RF-HOME-01 | Home pública em `/` com cabeçalho premium, sem expor links internos além de "Acesso interno". |
| RF-HOME-02 | Hero com CTA "Explorar produtos" levando ao catálogo público. |
| RF-HOME-03 | Faixa de benefícios abaixo do hero, consistente entre breakpoints. |
| RF-HOME-04 | Cards de categorias (imagem + nome) com categorias ativas públicas. |
| RF-HOME-05 | Vitrine responsiva de produtos com dados reais do catálogo. |
| RF-HOME-06 | Rodapé institucional consistente. |
| RF-HOME-07 | Acesso interno relocado de `/` para `/interno`, sem mudança de comportamento. |
| RF-HOME-08 | A home não altera rotas, dados, regras, autenticação/autorização nem eventos de State. |

### 2.3 Catálogo público — `public-catalog/spec.md` (Implementado)
| ID | Requisito |
|----|-----------|
| RF-CAT-01 | Visitantes consultam produtos `ATIVO` e dados gerais; somente leitura, sem autenticação. |
| RF-CAT-02 | Navegação por categorias `ATIVO`; categorias inativas não são oferecidas. |
| RF-CAT-03 | Detalhes de produto `ATIVO` com variações `ATIVO`, preço e estoque; estoque zero = indisponível para compra. |
| RF-CAT-04 | Imagem principal entregue por URL assinada temporária, sem expor caminho privado. |
| RF-CAT-05 | Falhas públicas são observáveis (sem sucesso simulado) e permitem nova tentativa. |

### 2.4 Carrinho — `shopping-cart/spec.md` (Implementado)
| ID | Requisito |
|----|-----------|
| RF-CART-01 | Carrinho persistente por Cliente `ATIVO`, isolado por proprietário. |
| RF-CART-02 | Adicionar/atualizar/remover itens; quantidade inteira > 0 e ≤ estoque; uma variação por carrinho. |
| RF-CART-03 | Operações respeitam status de produto/variação/estoque atuais, sem reservar estoque. |
| RF-CART-04 | Subtotal/total calculados com o preço atual; preço do cliente é ignorado. |
| RF-CART-05 | Interface via State/Python; tokens fora do navegador; falhas observáveis. |

### 2.5 Checkout e Pedidos — change `checkout-pedidos` (`checkout-orders`) (Em andamento)
| ID | Requisito |
|----|-----------|
| RF-ORD-01 | Cliente revisa o carrinho e seleciona endereço próprio ativo para confirmar. |
| RF-ORD-02 | Produto, variação, preço e estoque são revalidados na confirmação; exigir nova revisão se mudar. |
| RF-ORD-03 | Criação atômica de Pedido + ItemPedido + Pagamento `PENDENTE` (valor = total, frete zero). |
| RF-ORD-04 | Carrinho é esvaziado após sucesso; consulta owner-scoped de pedidos e resumos. |
| RF-ORD-05 | Sem baixa/reserva de estoque nesta change (apenas revalidação). A baixa/devolução de estoque no Pedido é **decisão pendente** (`docs/domain-model.md` §5.3 e §8, regra 17). |

### 2.6 Pagamento (simulado) — `order-payment/spec.md` (Implementado)
| ID | Requisito |
|----|-----------|
| RF-PAY-01 | Cliente `ATIVO` simula aprovação do próprio pedido elegível; Pagamento→`APROVADO`, Pedido→`PAGAMENTO_CONFIRMADO`. |
| RF-PAY-02 | Preserva o contrato do Pagamento (método/valor, sem parcial, sem histórico de tentativas). |
| RF-PAY-03 | Aprovação não altera inventário. |
| RF-PAY-04 | Status confirmado exibido via State; falhas não exibem aprovação. |

### 2.7 Acesso interno — `internal-access/spec.md` (Implementado)
| ID | Requisito |
|----|-----------|
| RF-INT-01 | Login apenas de `UsuarioInterno` provisionado; sem cadastro público. |
| RF-INT-02 | Identidade interna usa perfis `FUNCIONARIO`/`ADMINISTRADOR` e status `ATIVO`/`INATIVO`. |
| RF-INT-03 | Acesso à área protegida apenas para sessão válida `ATIVO`, autorizado no backend. |
| RF-INT-04 | Logout remove a sessão local e encerra o acesso. |
| RF-INT-05 | Acesso interno é separado do acesso de Cliente. |

### 2.8 Gestão de catálogo — `catalog-management/spec.md` (Implementado)
| ID | Requisito |
|----|-----------|
| RF-CATM-01 | Administradores gerenciam categorias (nome obrigatório/único, status; novos `ATIVO`). |
| RF-CATM-02 | Administradores gerenciam marcas (nome obrigatório/único, status; novos `ATIVO`). |
| RF-CATM-03 | Categorias/marcas são inativadas, não excluídas. |
| RF-CATM-04 | Gestão restrita a `ADMINISTRADOR` (autorização no backend). |
| RF-CATM-05 | Erros de gestão permanecem observáveis; dados preservados em falha. |

### 2.9 Gestão de clientes e endereços — change `cadastro-cliente-enderecos` (`customer-access`, `customer-addresses`) (Em andamento)
| ID | Requisito |
|----|-----------|
| RF-CUST-01 | Cadastro de Cliente com CPF/e-mail únicos, credenciais protegidas e status. |
| RF-CUST-02 | Login e sessão de Cliente independentes do acesso interno; bloqueio de inativo. |
| RF-CUST-03 | Cliente consulta/edita apenas os próprios dados; CPF não é livremente alterável. |
| RF-CUST-04 | CRUD de Endereco próprio, com no máximo um principal e preservação quando usado em Pedido. |

### 2.10 Gestão de produtos — change `gestao-produtos` (`product-management`) (Em andamento)
| ID | Requisito |
|----|-----------|
| RF-PROD-01 | Administrador lista/cria/edita/inativa produtos; histórico comercial preservado. |
| RF-PROD-02 | Cada Produto pertence a exatamente uma Categoria e uma Marca existentes. |
| RF-PROD-03 | Cada Produto possui ao menos uma `VariacaoProduto` (SKU único, preço > 0, estoque ≥ 0, status). |
| RF-PROD-04 | Imagem principal única opcional armazenada no Xano. |
| RF-PROD-05 | Autorização de `ADMINISTRADOR` validada no backend. |

### 2.11 Interface visual — `visual-interface/spec.md` (Implementado)
| ID | Requisito |
|----|-----------|
| RF-UI-01 | Identidade visual única (navy/ciano/superfícies claras) em todas as páginas. |
| RF-UI-02 | Superfícies de produto claras e consistentes, sem alterar elegibilidade/dados. |
| RF-UI-03 | Fluxos de conta e compra com componentes responsivos reutilizáveis. |
| RF-UI-04 | Formulários/listas administrativos mantêm os limites de papel existentes. |
| RF-UI-05 | Cabeçalho/rodapé responsivos apontando apenas a rotas existentes. |
| RF-UI-06 | Estados de feedback (loading/erro/sucesso/vazio/indisponível) e foco visível. |
| RF-UI-07 | A reformulação visual não altera comportamento de negócio. |

### 2.12 CRM / Atendimento — `docs/project-overview.md` §6.3; `docs/domain-model.md` §6.1 (**Pendente**)
| ID | Requisito |
|----|-----------|
| RF-CRM-01 | Consultar informações de clientes e histórico de compras no CRM. — **pendente (sem spec)** |
| RF-CRM-02 | Registrar e consultar atendimentos (assunto, descrição, status, responsável). — **pendente (sem spec)** |
| RF-CRM-03 | Associar atendimento a Pedido do mesmo Cliente (opcional). — **pendente (sem spec)** |

## 3. Requisitos Não Funcionais (RNF)

### 3.1 RNF documentados / implícitos
| ID | Categoria | Requisito | Evidência |
|----|-----------|-----------|-----------|
| RNF-01 | Segurança (autorização) | Regras de autorização aplicadas no backend, não só na interface. | `project-overview.md` §10; `internal-access/spec.md`; `catalog-management/spec.md` |
| RNF-02 | Segurança (sessão) | Sessões de Cliente e de `UsuarioInterno` separadas. | `internal-access/spec.md` RF-INT-05; change `cadastro-cliente-enderecos` |
| RNF-03 | Segurança (segredos) | Sem credenciais/tokens no código versionado; configuração por ambiente. | `reflex-xano-integration/spec.md` RF-XANO-03 |
| RNF-04 | Confiabilidade (observabilidade) | Falhas de rede/HTTP/resposta são apresentadas como falha, sem sucesso simulado. | `public-catalog/spec.md` RF-CAT-05; `shopping-cart/spec.md` RF-CART-05; `order-payment/spec.md` RF-PAY-04; `reflex-xano-integration/spec.md` |
| RNF-05 | Usabilidade | Componentes responsivos, legíveis e sem overflow; adaptação a mobile. | `visual-interface/spec.md`; `public-home/spec.md` |
| RNF-06 | Acessibilidade | Foco de teclado visível e contraste de texto adequado. | `visual-interface/spec.md` RF-UI-06 |
| RNF-07 | Integridade/consistência | Consistência e integridade de dados entre e-commerce e CRM. | `project-overview.md` §7/§10; `domain-model.md` §8 |
| RNF-08 | Manutenibilidade/processo | Desenvolvimento incremental, revisão antes da implementação e rastreabilidade via OpenSpec + Git. | `project-overview.md` §8/§9/§11; `AGENTS.md` |

### 3.2 RNF não definidos (lacunas — a definir)
Registrados para transparência; **não há metas documentadas** e nenhuma foi inventada. A ausência de métricas é uma lacuna assumida; estes itens permanecem **a definir**.

| ID | Categoria | Situação |
|----|-----------|----------|
| RNF-09 | Desempenho (tempo de resposta, throughput) | **A definir** |
| RNF-10 | Disponibilidade (SLA/uptime) | **A definir** |
| RNF-11 | Escalabilidade (carga, concorrência) | **A definir** |
| RNF-12 | Portabilidade (navegadores/dispositivos suportados) | **A definir** |
| RNF-13 | Manutenibilidade quantitativa (cobertura de testes, complexidade) | **A definir** |
| RNF-14 | Interoperabilidade (padrões de API) | **A definir** |
| RNF-15 | Localização/i18n (idiomas, moeda, fuso) | **A definir** |

> Nota: existem 6 arquivos de teste em `tests/` (`test_public_catalog.py`, `test_catalog_management.py`, `test_checkout_orders.py`, `test_customer_access.py`, `test_product_management.py`, `test_shopping_cart.py`), mas **não há meta de cobertura documentada**.

## 4. Casos de Uso (UC)

> Derivados dos cenários das specs. **Template:** ID, ator(es), pré-condições, **fluxo principal numerado**, **fluxos alternativos/exceções numerados**, pós-condições e referência à spec de origem. Nenhum passo novo de comportamento é introduzido.

### UC-01 — Consultar catálogo público
- **Ator(es):** Visitante.
- **Pré-condições:** nenhuma sessão exigida.
- **Fluxo principal:**
  1. O visitante abre o catálogo público.
  2. O sistema lista os produtos `ATIVO`.
  3. O visitante seleciona uma categoria `ATIVO` (opcional).
  4. O sistema filtra os produtos `ATIVO` da categoria.
  5. O visitante abre os detalhes de um produto `ATIVO`.
  6. O sistema exibe informações, variações `ATIVO`, preço e estoque.
- **Fluxos alternativos/exceções:**
  1. Categoria `INATIVO` não é oferecida como filtro.
  2. Produto inativo/inexistente retorna "não encontrado".
  3. Variação ativa com estoque zero é exibida como indisponível para compra (status preservado).
  4. Falha de carregamento é reportada, permitindo nova tentativa.
- **Pós-condições:** nenhuma alteração de dados (consulta somente leitura).
- **Referência:** `public-catalog/spec.md`.

### UC-02 — Manter o carrinho
- **Ator(es):** Cliente.
- **Pré-condições:** sessão de Cliente `ATIVO`.
- **Fluxo principal:**
  1. O cliente abre o carrinho (possivelmente vazio).
  2. O cliente adiciona uma variação `ATIVO` com estoque disponível.
  3. O sistema inclui o item com a quantidade solicitada.
  4. O cliente ajusta/remove itens.
  5. O sistema recalcula subtotais e total com o preço atual.
- **Fluxos alternativos/exceções:**
  1. Variação já presente: a quantidade é atualizada, sem duplicar linha.
  2. Quantidade zero: o item é removido.
  3. Quantidade fracionária/negativa/acima do estoque: rejeitada.
  4. Acesso ao carrinho de outro cliente: rejeitado.
  5. Item que fica indisponível: marcado e pode ser removido.
- **Pós-condições:** carrinho persistido do proprietário, sem reserva de estoque.
- **Referência:** `shopping-cart/spec.md`.

### UC-03 — Confirmar pedido (checkout)
- **Ator(es):** Cliente.
- **Pré-condições:** carrinho com itens válidos; cliente com endereço próprio ativo.
- **Fluxo principal:**
  1. O cliente revisa o carrinho e seleciona um endereço próprio ativo.
  2. O sistema revalida produto, variação, preço e estoque.
  3. O cliente confirma o pedido.
  4. O sistema cria atomicamente Pedido + ItemPedido + Pagamento `PENDENTE` (valor = total, frete zero).
  5. O sistema esvazia o carrinho.
- **Fluxos alternativos/exceções:**
  1. Preço/conteúdo mudou desde a revisão: exige nova revisão antes de criar o Pedido.
  2. Item/endereço inválido: o Pedido não é criado (sem efeitos parciais).
  3. Falha na criação: nenhuma entidade é persistida (atomicidade).
- **Pós-condições:** Pedido criado com Pagamento `PENDENTE`; carrinho vazio.
- **Referência:** change `checkout-pedidos` — `openspec/changes/checkout-pedidos/specs/checkout-orders/spec.md`.

### UC-04 — Simular pagamento do pedido
- **Ator(es):** Cliente.
- **Pré-condições:** pedido próprio com Pagamento `PENDENTE` e status `AGUARDANDO_PAGAMENTO`.
- **Fluxo principal:**
  1. O cliente abre o pedido elegível.
  2. O cliente solicita a simulação de pagamento.
  3. O sistema aprova o Pagamento (`APROVADO`).
  4. O sistema move o Pedido para `PAGAMENTO_CONFIRMADO`.
  5. O sistema exibe o status confirmado.
- **Fluxos alternativos/exceções:**
  1. Pedido de outro cliente: rejeitado sem revelar dados.
  2. Estado não elegível: nenhum registro é alterado.
  3. Repetição após aprovação: retorna o estado atual, sem criar novo Pagamento.
  4. Falha: a aprovação não é exibida.
- **Pós-condições:** Pagamento `APROVADO` e Pedido `PAGAMENTO_CONFIRMADO`; inventário inalterado.
- **Referência:** `order-payment/spec.md`.

### UC-05 — Autenticar usuário interno
- **Ator(es):** Funcionário, Administrador.
- **Pré-condições:** `UsuarioInterno` provisionado no Xano com status `ATIVO`.
- **Fluxo principal:**
  1. O usuário abre `/interno`.
  2. Informa credenciais.
  3. O backend autentica e cria a sessão.
  4. O usuário acessa a área conforme o perfil.
- **Fluxos alternativos/exceções:**
  1. Credenciais inválidas: falha de autenticação.
  2. Usuário `INATIVO`: acesso negado.
  3. Sem sessão: a área protegida não é apresentada.
  4. Logout: a sessão é encerrada.
- **Pós-condições:** sessão interna ativa (ou encerrada no logout).
- **Referência:** `internal-access/spec.md`.

### UC-06 — Gerenciar categorias e marcas
- **Ator(es):** Administrador.
- **Pré-condições:** sessão `ADMINISTRADOR` `ATIVO`.
- **Fluxo principal:**
  1. O administrador lista categorias/marcas.
  2. Cria/edita um registro com nome único.
  3. O sistema salva o registro como `ATIVO`.
  4. O administrador inativa/reativa conforme necessário.
- **Fluxos alternativos/exceções:**
  1. Nome ausente/duplicado: rejeitado.
  2. Perfil `FUNCIONARIO` ou não autenticado: rejeitado no backend.
  3. Sem exclusão definitiva: registros são preservados.
- **Pós-condições:** registro criado/atualizado e preservado (nunca excluído).
- **Referência:** `catalog-management/spec.md`.

### UC-07 — Cadastrar e autenticar Cliente
- **Ator(es):** Cliente.
- **Pré-condições:** nenhuma (cadastro); conta existente `ATIVO` (login).
- **Fluxo principal:**
  1. O cliente informa dados válidos (CPF/e-mail únicos, senha).
  2. O sistema cria a conta.
  3. O cliente autentica e obtém a sessão de Cliente.
  4. O cliente gerencia os próprios dados e endereços.
- **Fluxos alternativos/exceções:**
  1. CPF/e-mail duplicado: cadastro rejeitado.
  2. Cliente `INATIVO`: acesso bloqueado.
  3. Tentativa de alterar CPF livremente: bloqueada.
- **Pós-condições:** conta de Cliente ativa e sessão de Cliente estabelecida.
- **Referência:** change `cadastro-cliente-enderecos` — `openspec/changes/cadastro-cliente-enderecos/specs/customer-access/spec.md` e `openspec/changes/cadastro-cliente-enderecos/specs/customer-addresses/spec.md`.

## 5. Matriz de rastreabilidade (resumo)

| Área | RF | UC | Spec/Origem | Status |
|------|----|----|-------------|--------|
| Integração Reflex↔Xano | RF-XANO-01..04 | — | `reflex-xano-integration` | Implementado |
| Home pública | RF-HOME-01..08 | — | `public-home` | Implementado |
| Catálogo público | RF-CAT-01..05 | UC-01 | `public-catalog` | Implementado |
| Carrinho | RF-CART-01..05 | UC-02 | `shopping-cart` | Implementado |
| Checkout/Pedidos | RF-ORD-01..05 | UC-03 | change `checkout-pedidos` | Em andamento |
| Pagamento | RF-PAY-01..04 | UC-04 | `order-payment` | Implementado |
| Acesso interno | RF-INT-01..05 | UC-05 | `internal-access` | Implementado |
| Gestão de catálogo | RF-CATM-01..05 | UC-06 | `catalog-management` | Implementado |
| Cliente/Endereços | RF-CUST-01..04 | UC-07 | change `cadastro-cliente-enderecos` | Em andamento |
| Gestão de produtos | RF-PROD-01..05 | — | change `gestao-produtos` | Em andamento |
| Interface visual | RF-UI-01..07 | — | `visual-interface` | Implementado |
| CRM/Atendimento | RF-CRM-01..03 | — | `project-overview.md` §6.3 | Pendente |

## 6. Pendências e lacunas

1. **CRM/Atendimento sem comportamento especificado** (RF-CRM-01..03) — principal lacuna funcional.
2. **RNF quantitativos ausentes** (RNF-09..15) — desempenho, disponibilidade, escalabilidade, portabilidade, manutenibilidade, interoperabilidade e localização não possuem metas.
3. **Verificação de requisitos com usuários não realizada** — ver `01-elicitacao-requisitos.md` §4.
