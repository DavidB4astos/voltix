# 01 — Elicitação de Requisitos

> Documento da AP2 — Voltix. Entrega: 21/10/2026.
> Fontes: `docs/project-overview.md`, `docs/domain-model.md`, `AGENTS.md`, `openspec/config.yaml`, `openspec/specs/`, `openspec/changes/`, `xano/`, `tests/`, `docs/referencias/`.

## 1. Objetivo

Registrar **como os requisitos do Voltix foram levantados e refinados**, identificando as técnicas efetivamente utilizadas e suas evidências reais no repositório. Este documento **não** descreve entrevistas, questionários ou resultados com usuários, porque essas atividades **não foram realizadas** no projeto até o momento (ver §4).

## 2. Contexto do levantamento

O Voltix é um projeto acadêmico conduzido por uma equipe discente, com desenvolvimento incremental orientado por especificações (OpenSpec) e stack definida previamente (Reflex + Xano). As fontes primárias de requisitos são os documentos do próprio projeto e as regras da disciplina registradas em `AGENTS.md` e `openspec/config.yaml`. Não há, no repositório, registro de interação com clientes ou usuários externos.

## 3. Técnicas de elicitação efetivamente utilizadas

| # | Técnica | Aplicada | Evidência real | Como foi utilizada |
|---|---------|----------|----------------|--------------------|
| T1 | Análise documental e de restrições do projeto | Sim | `AGENTS.md`; `openspec/config.yaml` (context/rules); `docs/project-overview.md` | Levantar visão, escopo, usuários, funcionalidades e restrições a partir dos documentos-fonte e das regras da disciplina |
| T2 | Modelagem de domínio | Sim | `docs/domain-model.md` (13 conceitos, relacionamentos, regras estruturais e §9 "conceitos fora do modelo") | Identificar entidades, atributos conceituais, cardinalidades e regras que originam requisitos |
| T3 | Especificação orientada a comportamento (cenários) | Sim | `openspec/specs/*/spec.md` (43 requisitos, cada um com `#### Scenario:` no formato WHEN/THEN) | Converter objetivos em requisitos verificáveis (`SHALL`) com critérios de aceitação por cenário |
| T4 | Decomposição incremental em mudanças | Sim | `openspec/changes/` — 5 changes ativas e 8 arquivadas, cada uma com `proposal.md`, `design.md`, `tasks.md` e seção "Ficam fora do escopo" | Refinar o escopo em incrementos pequenos, delimitando explicitamente o que entra e o que fica fora |
| T5 | Análise de referências visuais | Sim | `docs/referencias/` (3 imagens de referência); change arquivada `2026-10-13-design-interface-voltix`; spec `visual-interface` | Orientar identidade visual e requisitos de interface a partir de referências de design |
| T6 | Verificação exploratória da API pública publicada | Sim | Change `conectar-catalogo-publico-xano`; `xano/api/public_catalog/*.xs`; `xano/table/` (persistência de `produto`/`variacao_produto`); `.env.example` (chaves `XANO_PUBLIC_*`) | Inspecionar os endpoints públicos já publicados no Xano (categorias, produtos, detalhes e imagem), por leitura anônima e somente leitura, para confirmar o contrato consumido pelo frontend |

### T3 — Detalhamento

Cada requisito em `openspec/specs/` é escrito como afirmação verificável (`SHALL`) seguida de cenários de aceitação (ex.: `public-catalog/spec.md` possui 5 requisitos; `shopping-cart/spec.md` possui 5). Essa técnica é a principal origem dos critérios de aceitação usados nas User Stories (`02-user-stories.md`).

### T4 — Detalhamento

Exemplos de delimitação de escopo registrados nas próprias changes:
- `checkout-pedidos`: "Ficam fora do escopo pagamento real ou fluxo de aprovação, gateway, cotação/integração de frete, CRM e gerenciamento administrativo de Pedidos."
- `cadastro-cliente-enderecos`: "Ficam fora do escopo: recuperação de senha, exclusão de Cliente, carrinho, checkout, pedidos, pagamento, CRM…"
- `gestao-produtos`: "Ficam fora desta Change: catálogo público, pesquisa, carrinho, pedidos, pagamentos, CRM…"

### T5 — Detalhamento

As três imagens em `docs/referencias/` orientaram a identidade visual e o layout premium da vitrine, consolidados na spec `visual-interface` e na change arquivada `2026-10-13-design-interface-voltix`: paleta navy/ciano/ciano-escuro sobre superfícies claras, cabeçalho e rodapé institucionais, cards de categoria e vitrine de produtos responsivos, e estados de feedback com foco visível. A descrição aqui é textual e deriva do que foi efetivamente consolidado na spec e na change — não de uma leitura interpretativa do conteúdo das imagens.

### T6 — Detalhamento

A change `conectar-catalogo-publico-xano` documenta a base pública `https://x8ki-letl-twmt.n7.xano.io/api:cVn4Vybh` e os caminhos `/categories`, `/products`, `/products/{product_id}` e `/products/{product_id}/image`. A verificação foi feita por consulta anônima de leitura (sem autenticação), alinhada à restrição de manter as requisições públicas anônimas e somente de leitura. Nenhum dado foi criado ou alterado durante a verificação.

## 4. Técnicas de elicitação NÃO utilizadas

Registradas explicitamente para evitar resultados fabricados. **Não há evidência** destas técnicas no repositório:

| Técnica | Situação |
|---------|----------|
| Entrevistas com clientes/usuários | Não realizada |
| Questionários/surveys | Não realizada |
| Observação direta / etnografia | Não realizada |
| Prototipação com usuários e testes de usabilidade | Não realizada |
| Brainstorming / grupo focal com stakeholders externos | Não realizada |
| Priorização formal com stakeholders (ex.: Planning Poker, votação com cliente) | Não realizada |

A priorização por valor, esforço e risco (`04-priorizacao-moscow.md`) foi produzida **pela própria equipe**, com base no estado documentado do projeto, e não a partir de input formal de stakeholders.

## 5. Fontes inventariadas (rastreabilidade)

| Fonte | Papel no levantamento |
|-------|-----------------------|
| `AGENTS.md` | Regras de projeto, arquitetura e processo |
| `openspec/config.yaml` | Contexto e regras dos workflows OpenSpec |
| `docs/project-overview.md` | Visão, problema, objetivos, público-alvo, escopo, funcionalidades, restrições |
| `docs/domain-model.md` | Conceitos, relacionamentos e regras de domínio |
| `openspec/specs/` | 8 capabilities / 43 requisitos com cenários |
| `openspec/changes/` | 5 changes ativas + 8 arquivadas (incrementos e delimitação de escopo) |
| `docs/referencias/` | Referências visuais |
| `xano/api/`, `xano/table/` | Contratos técnicos e persistência (verificados na técnica T6) |
| `tests/` | Verificação automatizada dos cenários elicitados (apoio à técnica T3) |
| `.env.example` | Contrato de configuração por ambiente |

## 6. Lacunas e recomendações

- **Lacuna:** ausência de elicitação com usuários reais. Recomenda-se registrar, na AP2 ou em trabalho futuro, a validação de requisitos com representantes dos perfis Cliente/Funcionário/Administrador.
- **Lacuna:** requisitos de CRM (Atendimento) estão previstos em `docs/project-overview.md` §6.3 e `docs/domain-model.md` §6.1, mas ainda **não possuem spec** — não foram elicitados/refinados em nível de comportamento verificável.
- **Recomendação:** manter a técnica T3 (cenários) como fonte canônica dos critérios de aceitação e rastrear cada User Story à sua spec de origem.

## 7. Justificativa da abordagem de elicitação (documental / spec-driven)

A elicitação deste projeto foi **documental e orientada por especificações**, e essa escolha é adequada ao contexto por três razões objetivas:

1. **Fontes canônicas no repositório.** Visão, escopo, domínio e comportamento estão registrados de forma estruturada (`docs/project-overview.md`, `docs/domain-model.md`, `openspec/specs/`), permitindo derivar requisitos rastreáveis sem intermediários.
2. **Contexto acadêmico sem acesso a stakeholders.** O projeto é desenvolvido por uma equipe discente, sem clientes reais disponíveis para entrevistas; as regras da disciplina e do fluxo OpenSpec (`AGENTS.md`, `openspec/config.yaml`) definem o processo e o escopo.
3. **Verificabilidade incremental.** Cada incremento é especificado em cenários WHEN/THEN e validado por changes e testes, funcionando como mecanismo contínuo de confirmação de requisitos.

**Limitação explícita:** por não haver interação com usuários, **não houve validação de requisitos com representantes de Cliente, Funcionário ou Administrador**, nem entrevistas, questionários ou observação (ver §4). Essa é uma lacuna assumida e registrada, não um resultado fabricado. Recomenda-se, em trabalho futuro, complementar a elicitação documental com validação com usuários.
