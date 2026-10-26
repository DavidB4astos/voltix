# Roadmap de Changes Ã¢ÂÂ Voltix

Documento central de organizaÃÂ§ÃÂ£o do desenvolvimento.

Fontes: `AGENTS.md`, `docs/project-overview.md`, `docs/domain-model.md`, `openspec/config.yaml`, specs consolidadas, changes ativas/arquivadas, auditoria documental, cÃÂ³digo atual Reflex e XanoScript.

## Regras

- Implementar **UMA change por vez**. Sem paralelismo nem intercalamento.
- NÃÂ£o recriar changes arquivadas nem funcionalidades jÃÂ¡ existentes.
- Toda change encerrada (spec + implementaÃÂ§ÃÂ£o + testes) antes de abrir a prÃÂ³xima.
- Changes adiadas por bloqueio ou priorizaÃÂ§ÃÂ£o ficam em `docs/deferred-changes/YYYY-MM-DD-<name>/`, com README de status, bloqueio e retomada; nÃÂ£o sÃÂ£o ativas nem arquivadas como concluÃÂ­das.
- DecisÃÂµes E1Ã¢ÂÂE7 abaixo sÃÂ£o **aprovadas e nÃÂ£o sÃÂ£o reabertas**.
- **A aprovaÃÂ§ÃÂ£o deste roadmap NÃÂO autoriza criar nem implementar changes futuras. Cada change exige aprovaÃÂ§ÃÂ£o individual antes de qualquer criaÃÂ§ÃÂ£o OpenSpec ou alteraÃÂ§ÃÂ£o de cÃÂ³digo/Xano.**

## Estado atual

- **ENCERRADA (arquivada em 2026-10-23):** `refine-storefront-home` Ã¢ÂÂ implementaÃÂ§ÃÂ£o no working tree (nÃÂ£o commitada). **Escopo tÃÂ©cnico atual da Home: concluÃÂ­do tecnicamente** (estrutura editorial, CSS escopado em `.vx-home`, vitrine curada com proveniÃÂªncia, acessibilidade por inspeÃÂ§ÃÂ£o estÃÂ¡tica). 5.2 **PASSOU** em 2026-10-22 (multi-viewport). 5.3 **PASSOU** em 2026-10-23 (evidÃÂªncia visual do usuÃÂ¡rio): `/carrinho`, `/cliente` e `/interno` jÃÂ¡ haviam passado; `/catalogo` agora carrega e exibe os produtos normalmente, sem novo 429. A correÃÂ§ÃÂ£o mÃÂ­nima do fan-out de imagens foi **absorvida** nesta change (tarefas 7.1Ã¢ÂÂ7.8; delta `public-catalog`), e a antiga change `fix-catalog-image-n1` foi movida para `docs/superseded-changes/2026-10-22-fix-catalog-image-n1/`. A correÃÂ§ÃÂ£o jÃÂ¡ estÃÂ¡ implementada no working tree: 139 testes OK, `py_compile` e `reflex compile` OK. Em 2026-10-23, o endpoint publicado foi validado (`GET /products` 200, 23 ATIVO, `image_url` em 23/23, sem `imagem_principal`; todos nulos). A passagem final ÃÂºnica confirmou `/catalogo` com 23 cards, 3 imagens locais completas, **0 imagens quebradas** e 20 cards sem `<img>`; a Home exibiu hero, categorias, seÃÂ§ÃÂ£o editorial e vitrine. O servidor novo (PID 31912) manteve `reflex.err.log` com **0 linhas** e nenhum novo 429. Capturas: `voltix-final-catalogo-20261023.png` e `voltix-final-home-20261023.png`. A verificaÃÂ§ÃÂ£o efetiva de `AGENTS.md` ÃÂ§6 e `openspec/config.yaml` estÃÂ¡ concluÃÂ­da. Change **arquivada em 2026-10-23** em `openspec/changes/archive/2026-10-23-refine-storefront-home/`; a spec consolidada `public-home` foi preservada e o delta de `public-catalog` foi sincronizado. A **evoluÃÂ§ÃÂ£o visual premium da Home** fica para uma Change futura.
- **CORREÃÂÃÂO ABSORVIDA:** `fix-catalog-image-n1` nÃÂ£o foi implementada como change independente; seus artefatos foram preservados em `docs/superseded-changes/2026-10-22-fix-catalog-image-n1/` e nÃÂ£o devem ser recriados como change ativa.
- **PRÃXIMA PRIORIDADE:** pesquisa-catalogo (C5) Â busca textual por **nome do produto** no catÃ¡logo pÃºblico; zero dependÃªncias; inicia apÃ³s o encerramento de
efine-storefront-home. **CHANGE ATIVA/PROPOSTA VIA OPENSPEC:** openspec/changes/pesquisa-catalogo/ (0/11 tarefas) criada em 2026-10-23.
efine-storefront-home. **CHANGE ATIVA/PROPOSTA VIA OPENSPEC:** openspec/changes/pesquisa-catalogo/ (0/11 tarefas) criada em 2026-10-23.
- **ATIVA:** nenhuma. `imagens-reais-catalogo` foi **concluÃÂ­da (24/24 tarefas)**, **arquivada em 2026-10-19** (`openspec/changes/archive/2026-10-19-imagens-reais-catalogo/`) e **publicada em `origin/main`** (commits `f9688bd`, `9b31e67`), com as specs consolidadas atualizadas em `openspec/specs/public-catalog/spec.md`, `openspec/specs/public-home/spec.md` e `openspec/specs/visual-interface/spec.md` (+1 requisito cada). Entrega a infraestrutura de imagens locais dos produtos demo (VTX-DEMO-*) com detecÃÂ§ÃÂ£o automÃÂ¡tica de extensÃÂ£o (`.png/.jpg/.jpeg/.webp`) e fallback por nome exato; 3 de 20 imagens adicionadas (as 17 restantes sÃÂ£o **pendÃÂªncia de conteÃÂºdo**, nÃÂ£o de implementaÃÂ§ÃÂ£o). O armazenamento local ÃÂ© **provisÃÂ³rio**, sujeito ÃÂ  confirmaÃÂ§ÃÂ£o do professor sobre exigÃÂªncia de persistÃÂªncia no backend/banco. Antes disso, `catalog-loading-state` foi **concluÃÂ­da (10/10 tarefas)**, **arquivada em 2026-10-18** (`openspec/changes/archive/2026-10-18-catalog-loading-state/`) e **publicada em `origin/main`** (commits `54b3209`, `aadf2df`), com as specs consolidadas atualizadas em `openspec/specs/public-catalog/spec.md` (+1 requisito) e `openspec/specs/public-home/spec.md` (~1 requisito modificado). Corrige o flash "Nenhum produto disponÃÂ­vel" na primeira carga da Home e de `/catalogo` via flag `public_catalog_loaded`. Antes disso, `cadastro-produtos-em-massa` foi **concluÃÂ­da (17/17 tarefas)**, **arquivada em 2026-10-18** (`openspec/changes/archive/2026-10-18-cadastro-produtos-em-massa/`) e **publicada em `origin/main`** (commits `d7ef848`, `39039cb`), com a spec consolidada criada em `openspec/specs/product-bulk-import/spec.md`. Antes disso, `gestao-produtos` foi **concluÃÂ­da (15/15 tarefas)**, **arquivada em 2026-10-18** (`openspec/changes/archive/2026-10-18-gestao-produtos/`) e **publicada em `origin/main`** (commits `3421dc8`, `3b91921`). **LimitaÃÂ§ÃÂ£o conhecida:** o upload de imagem principal (`POST /products/{id}/image`) nÃÂ£o ÃÂ© operacional na instÃÂ¢ncia Xano Free (HTTP 403, `ERROR_CODE_ACCESS_DENIED`) Ã¢ÂÂ permanece **nÃÂ£o validado e nÃÂ£o declarado funcional**, dependendo de plano pago ou armazenamento externo gratuito a tratar em mudanÃÂ§a prÃÂ³pria.
- **ADIADA/BLOQUEADA (nÃÂ£o concluÃÂ­da):** `baixa-estoque-checkout` (C1) Ã¢ÂÂ 0/11 tarefas; artefatos preservados integralmente em `docs/deferred-changes/2026-10-23-baixa-estoque-checkout/`. Bloqueio: `db.direct_query` indisponÃÂ­vel no Xano Free. Retomada exige soluÃÂ§ÃÂ£o compatÃÂ­vel com o plano gratuito e nova aprovaÃÂ§ÃÂ£o explÃÂ­cita. NÃÂ£o ÃÂ© change ativa e nÃÂ£o foi arquivada.
- **ARQUIVADAS (20, concluÃÂ­das, nÃÂ£o recriar):** integracao-reflex-xano, acesso-interno, carrinho-compras, catalogo-publico, gestao-categorias-marcas, pagamento-pedido, design-interface-voltix, home-publica-voltix, resiliencia-catalogo-publico, cadastro-cliente-enderecos, checkout-pedidos, conectar-catalogo-publico-xano, documentacao-ap2, melhorar-ux-ui-ap2, validar-jornada-compra-e2e, gestao-produtos, cadastro-produtos-em-massa, catalog-loading-state, imagens-reais-catalogo, refine-storefront-home.

## DecisÃÂµes aprovadas (E1Ã¢ÂÂE7)

| # | DecisÃÂ£o |
|---|---|
| E1 | Cancelamento: cliente e `ADMINISTRADOR` atÃÂ© `PAGAMENTO_CONFIRMADO`; depois **apenas ADMINISTRADOR**, respeitando estados vÃÂ¡lidos e consistÃÂªncia pagamentos/estoque. |
| E2 | `FUNCIONARIO` pode consultar pedidos/clientes e registrar atendimentos. AlteraÃÂ§ÃÂµes sensÃÂ­veis sÃÂ£o exclusivas do `ADMINISTRADOR`. Matriz de autorizaÃÂ§ÃÂ£o no backend. |
| E3 | Dashboard de vendas obrigatÃÂ³rio (faturamento + quantidade de pedidos) Ã¢ÂÂ change C10. |
| E4 | CPF mascarado por padrÃÂ£o. Nunca expor senhas, hashes ou tokens. |
| E5 | Limites Xano Free verificados (abaixo). Consumo real pendente de mediÃÂ§ÃÂ£o no dashboard. |
| E6 | Compra E2E com mutaÃÂ§ÃÂµes **somente** em ambiente de testes isolado e autorizado. **NÃÂ£o presumir** que uma branch Xano isola os dados. |
| E7 | Testes focados por change; E2E somente quando necessÃÂ¡rio. |

## Limites Xano Free (E5, verificado)

| Item | Limite documentado |
|---|---|
| RequisiÃÂ§ÃÂµes API | 10 req / 20 s (`ERROR_CODE_TOO_MANY_REQUESTS`) |
| Registros (Postgres) | 100.000 |
| Workspaces | 1 |
| Ambientes isolados | NÃÂ£o disponÃÂ­veis (recurso pago) |
| APIs / funÃÂ§ÃÂµes | Ilimitadas (rate-limited) |

**NÃÂ£o verificÃÂ¡vel daqui:** consumo real de registros e histÃÂ³rico de rate limit. Medir no dashboard Xano (read-only) antes de **C7** e **C9** e registrar o resultado.

## Matriz de autorizaÃÂ§ÃÂ£o

PadrÃÂ£o do repo: interno = `auth="user"` + `role`/`status`; cliente = `auth="CLIENTE"` + precondition `cliente_id == $auth.id`.

| OperaÃÂ§ÃÂ£o | CLIENTE | FUNCIONARIO | ADMINISTRADOR |
|---|---|---|---|
| CatÃÂ¡logo pÃÂºblico e busca (C5) | Ã¢ÂÂ | Ã¢ÂÂ | Ã¢ÂÂ |
| Carrinho, checkout, endereÃÂ§os, pedidos prÃÂ³prios | Ã¢ÂÂ | Ã¢ÂÂ | Ã¢ÂÂ |
| Cancelar pedido Ã¢ÂÂ¤ `PAGAMENTO_CONFIRMADO` (E1) | Ã¢ÂÂ | Ã¢ÂÂ | Ã¢ÂÂ |
| Cancelar pedido > `PAGAMENTO_CONFIRMADO` (E1) | Ã¢ÂÂ | Ã¢ÂÂ | Ã¢ÂÂ |
| Listar/ver todos os pedidos (C3) | Ã¢ÂÂ | Ã¢ÂÂ | Ã¢ÂÂ |
| TransiÃÂ§ÃÂ£o `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE` | Ã¢ÂÂ | pendÃÂªncia C3 | Ã¢ÂÂ |
| Listar/ver clientes, CPF mascarado (C4) | Ã¢ÂÂ | Ã¢ÂÂ | Ã¢ÂÂ |
| Registrar/editar atendimento `ABERTO`/`EM_ATENDIMENTO` (C7) | Ã¢ÂÂ | Ã¢ÂÂ | Ã¢ÂÂ |
| Finalizar/cancelar atendimento | Ã¢ÂÂ | pendÃÂªncia C7 | Ã¢ÂÂ |
| Dashboard de vendas, leitura (C10) | Ã¢ÂÂ | pendÃÂªncia C10 | Ã¢ÂÂ |
| CRUD produtos/categorias/marcas (jÃÂ¡ vigente); upload de imagem **indisponÃÂ­vel no Xano Free** | Ã¢ÂÂ | Ã¢ÂÂ | Ã¢ÂÂ |

PendÃÂªncias sÃÂ£o detalhadas no `design` da respectiva change na hora da implementaÃÂ§ÃÂ£o; nÃÂ£o reabrem E2.

## Riscos tÃÂ©cnicos registrados

1. **Atomicidade de estoque (C1):** baixa multi-step em `checkout_confirm`; falha no meio nÃÂ£o pode deixar pedido persistido. MitigaÃÂ§ÃÂ£o: prÃÂ©-condiÃÂ§ÃÂ£o + `db.patch` guardado (`quantidade_disponivel >= q`) dentro da transaÃÂ§ÃÂ£o; rejeitar o pedido inteiro; teste de concorrÃÂªncia da ÃÂºltima unidade.
2. **Cancelamento e devoluÃÂ§ÃÂ£o (C2):** devoluÃÂ§ÃÂ£o idempotente; duplo cancelamento nÃÂ£o pode duplicar estoque; preservar pagamento 1:1 e histÃÂ³rico.
3. **Isolamento E2E (C9/E6):** sem ambiente Xano isolado no Free (1 workspace, sem ambientes isolados). **Dados efÃÂªmeros e limpeza em instÃÂ¢ncia compartilhada nÃÂ£o equivalem a isolamento** Ã¢ÂÂ ver bloqueio da C9. Complementar: rate limit 10 req/20 s exige `workers=1` e throttle.
4. **ConsistÃÂªncia pedidos/pagamentos/estoque:** ordem obrigatÃÂ³ria baixa (C1) Ã¢ÂÂ devoluÃÂ§ÃÂ£o (C2) Ã¢ÂÂ transiÃÂ§ÃÂµes (C3) Ã¢ÂÂ agregados (C10). Nenhuma mudanÃÂ§a de status sem regra de estoque resolvida.

## Ordem sequencial recomendada

```
F0  gestao-produtos (CONCLUÃÂDA 15/15, arquivada 2026-10-18)
F1  cadastro-produtos-em-massa (CONCLUÃÂDA 17/17, arquivada 2026-10-18)
F2  catalog-loading-state (CONCLUÃÂDA 10/10, arquivada 2026-10-18)
 1  C1  baixa-estoque-checkout
 2  C2  cancelamento-pedido
 3  C3  gestao-pedidos-painel
 4  C10 dashboard-vendas
 5  C4  consulta-clientes-painel
 6  C5  pesquisa-catalogo          (zero dependÃÂªncias; pode subir para 1 se priorizado)
 7  C6  crm-cliente-historico
 8  C7  crm-atendimentos           Ã¢ÂÂ exige mediÃÂ§ÃÂ£o E5 no dashboard
 9  C8  cobertura-testes-qualidade
10  C9  e2e-compra-completa        Ã¢ÂÂ BLOQUEADO: ver item C9
```

## SobreposiÃÂ§ÃÂµes evitadas

- C2 fornece o endpoint/regra de cancelamento; C3 apenas o consome.
- C4 entrega a leitura de clientes; C6 reutiliza-a como porta de entrada.
- C3 e C6 reutilizam os endpoints de pedidos existentes.
- C5 estende `products_GET` existente; nÃÂ£o cria novo grupo de API.
- Nada jÃÂ¡ existente deve ser recriado: catÃÂ¡logo pÃÂºblico, auth interna, auth de cliente, endereÃÂ§os, carrinho, checkout, pedidos, pagamento simulado, gestÃÂ£o de produtos/categorias/marcas, UI de status e botÃÂµes.

## Changes planejadas

Status: **- **PRÃXIMA PRIORIDADE:** pesquisa-catalogo (C5) Â busca textual por **nome do produto** no catÃ¡logo pÃºblico; zero dependÃªncias; inicia apÃ³s o encerramento de
efine-storefront-home. **CHANGE ATIVA/PROPOSTA VIA OPENSPEC:** openspec/changes/pesquisa-catalogo/ (0/11 tarefas) criada em 2026-10-23.

### C1 baixa-estoque-checkout

- **Status:** ADIADA/BLOQUEADA (nÃÂ£o concluÃÂ­da; 0/11 tarefas). Artefatos preservados em `docs/deferred-changes/2026-10-23-baixa-estoque-checkout/`; nÃÂ£o ÃÂ© change ativa. Retomada condicionada a soluÃÂ§ÃÂ£o compatÃÂ­vel com Xano Free e nova aprovaÃÂ§ÃÂ£o.

- **Objetivo:** baixar `quantidade_disponivel` na confirmaÃÂ§ÃÂ£o do pedido.
- **Requisitos:** domÃÂ­nio 5.1/5.2/8.15/8.17; overview 6.1.
- **Funcionalidades:** baixa transacional; prÃÂ©-condiÃÂ§ÃÂ£o de disponibilidade; contrato de resposta inalterado.
- **ExcluÃÂ­do:** cancelamento, reserva, movimentaÃÂ§ÃÂ£o de estoque, painel.
- **Regras:** inteiro Ã¢ÂÂ¥ 0; 0 = indisponÃÂ­vel mas ativo; falha = pedido inteiro negado; carrinho nÃÂ£o reserva.
- **DependÃÂªncias:** `checkout_confirm_POST.xs`; `test_checkout_orders.py`.
- **Aceite:** sem estoque Ã¢ÂÂ 400 e nada persistido; com estoque Ã¢ÂÂ baixa exata; **suÃÂ­te aplicÃÂ¡vel completa aprovada, sem regressÃÂµes**; teste de concorrÃÂªncia da ÃÂºltima unidade.
- **PendÃÂªncias:** formato do erro de indisponibilidade; log de baixa.

### C2 cancelamento-pedido

- **Objetivo:** cancelar pedido por cliente/ADMIN e devolver estoque (E1).
- **Requisitos:** domÃÂ­nio 5.3/8.17; overview 4.1/4.2.
- **Funcionalidades:** endpoint de cancel; regra de estados; devoluÃÂ§ÃÂ£o idempotente; UI em `/pedidos`.
- **ExcluÃÂ­do:** painel de gestÃÂ£o, reembolso real, logÃÂ­stica.
- **Regras:** E1; pagamento 1:1 preservado; histÃÂ³rico preservado; devolver somente se baixado (depende de C1).
- **DependÃÂªncias:** C1 (obrigatÃÂ³ria).
- **Aceite:** cancel em `AGUARDANDO_PAGAMENTO` devolve estoque exato; pÃÂ³s-`PAGAMENTO_CONFIRMADO` sÃÂ³ ADMIN; estados invÃÂ¡lidos rejeitados; cliente nÃÂ£o cancela pedido alheio; duplo cancel idempotente; suÃÂ­te completa sem regressÃÂµes.
- **PendÃÂªncias:** mensagem/UI de confirmaÃÂ§ÃÂ£o; efeito sobre status do `Pagamento`.

### C3 gestao-pedidos-painel

- **Objetivo:** listar/ver pedidos no painel e aplicar transiÃÂ§ÃÂµes `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE`.
- **Requisitos:** overview 4.2/6.2; domÃÂ­nio 5.3.
- **Funcionalidades:** `GET /admin/orders`, `GET /admin/orders/{id}`, `PATCH /admin/orders/{id}/status`; UI no painel.
- **ExcluÃÂ­do:** transportadora, mÃÂ©tricas (C10), CRM.
- **Regras:** transiÃÂ§ÃÂµes apenas no sentido vÃÂ¡lido; cancelamento via C2 (sem duplicar devoluÃÂ§ÃÂ£o); autorizaÃÂ§ÃÂ£o no backend.
- **DependÃÂªncias:** C1, C2.
- **Aceite:** FUNCIONARIO/ADMIN conforme matriz; transiÃÂ§ÃÂ£o invÃÂ¡lida rejeitada; cliente negado; autorizaÃÂ§ÃÂ£o negativa completa; suÃÂ­te sem regressÃÂµes.
- **PendÃÂªncias:** permissÃÂ£o de transiÃÂ§ÃÂ£o para FUNCIONARIO (detalhar no design).

### C10 dashboard-vendas

- **Objetivo:** painel com faturamento e quantidade de pedidos (E3).
- **Requisitos:** overview 4.2 ("acompanhar informaÃÂ§ÃÂµes relacionadas ÃÂ s vendas").
- **Funcionalidades:** agregados (total de pedidos, faturamento) por perÃÂ­odo; UI no painel; leitura apenas.
- **ExcluÃÂ­do:** grÃÂ¡ficos avanÃÂ§ados, exportaÃÂ§ÃÂµes, metas, previsÃÂ£o, CRM.
- **Regras:** faturamento = soma dos totais de pedidos nÃÂ£o cancelados/nÃÂ£o aguardando; sem dados sensÃÂ­veis (E4).
- **DependÃÂªncias:** C1, C2, C3 (statuses corretos).
- **Aceite:** valores corretos em fixtures; FUNCIONARIO conforme matriz; cliente negado; sem efeitos de estado; suÃÂ­te sem regressÃÂµes.
- **PendÃÂªncias:** perÃÂ­odo padrÃÂ£o; quais statuses entram no faturamento (detalhar no design).

### C4 consulta-clientes-painel

- **Objetivo:** lista e detalhe de clientes no painel (somente leitura).
- **Requisitos:** overview 5.1/6.2; domÃÂ­nio 4.1.
- **Funcionalidades:** `GET /admin/customers`, `GET /admin/customers/{id}`; UI.
- **ExcluÃÂ­do:** editar/inativar cliente, CRM, histÃÂ³rico (C6), exportaÃÂ§ÃÂ£o.
- **Regras:** CPF mascarado (E4); nunca senha/hash/token; cliente inativo preserva histÃÂ³rico.
- **DependÃÂªncias:** padrÃÂ£o de auth interno existente.
- **Aceite:** FUNCIONARIO/ADMIN conforme matriz; cliente negado; payload sem credenciais; suÃÂ­te sem regressÃÂµes.
- **PendÃÂªncias:** paginaÃÂ§ÃÂ£o; campos expostos.

### C5 pesquisa-catalogo

- **Status:** CONCLUÍDA E ARQUIVADA (2026-10-23) em openspec/changes/archive/2026-10-23-pesquisa-catalogo/. Publicada no Xano pi/public_catalog/products_GET.xs (UPDATE query products GET). Busca parcial case-insensitive por nome via q, combinável com category_id, termo vazio ignorado; cache atualizado por (categoria,q); UI no catálogo; testes ampliados e validados.
### C6 crm-cliente-historico

- **Objetivo:** no painel, consultar cliente Ã¢ÂÂ pedidos, itens, valores, status.
- **Requisitos:** overview 3/4.2/6.3; domÃÂ­nio 4.1/5.3.
- **Funcionalidades:** consulta de pedidos por `cliente_id` (uso interno) + UI de CRM.
- **ExcluÃÂ­do:** atendimentos (C7), ediÃÂ§ÃÂ£o de cliente, mÃÂ©tricas.
- **Regras:** histÃÂ³rico preservado; acesso restrito; consistÃÂªncia e-commerceÃ¢ÂÂCRM.
- **DependÃÂªncias:** C4, C3.
- **Aceite:** autorizaÃÂ§ÃÂ£o negativa; dados corretos de itens/totais; CPF mascarado; suÃÂ­te sem regressÃÂµes.
- **PendÃÂªncias:** volume de dados no Free; filtros por perÃÂ­odo/status.

### C7 crm-atendimentos

- **Objetivo:** criar a entidade e o fluxo de registro/consulta de atendimentos (domÃÂ­nio 6.1, regras 18/19/20).
- **Requisitos:** overview 3/4.2/6.3; domÃÂ­nio 19/20.
- **Funcionalidades:** tabela `atendimento`; CRUD com auth interna; UI de registro/histÃÂ³rico.
- **ExcluÃÂ­do:** `InteracaoAtendimento`/mensagens, SLA, automaÃÂ§ÃÂµes.
- **Regras:** sempre Cliente + UsuarioInterno; pedido opcional e do mesmo cliente; `ABERTO`/`EM_ATENDIMENTO` atualizÃÂ¡veis; `FINALIZADO`/`CANCELADO` imutÃÂ¡veis.
- **DependÃÂªncias:** C4, C6; mediÃÂ§ÃÂ£o E5 no dashboard (tabela nova).
- **Aceite:** regras 18/19/20 verificadas; pedido de outro cliente rejeitado; atendimento finalizado imutÃÂ¡vel; autorizaÃÂ§ÃÂ£o negativa; suÃÂ­te sem regressÃÂµes.
- **PendÃÂªncias:** quem pode finalizar (FUNCIONARIO?); provisionamento do 1ÃÂº usuÃÂ¡rio interno.

### C8 cobertura-testes-qualidade

- **Objetivo:** cobrir specs sem testes (`internal-access`, `reflex-xano-integration`).
- **Requisitos:** AGENTS seÃÂ§ÃÂ£o 6.
- **Funcionalidades:** `test_internal_access.py`; `test_integration_health.py`; regressÃÂ£o final.
- **ExcluÃÂ­do:** novas funcionalidades; axe-core (adiado).
- **Regras:** nÃÂ£o duplicar suÃÂ­tes existentes; testar apenas comportamento especificado.
- **DependÃÂªncias:** C1Ã¢ÂÂC7 concluÃÂ­das (validar o que jÃÂ¡ existir na ÃÂ©poca).
- **Aceite:** `unittest discover -s tests` verde; specs sem cobertura = 0.
- **PendÃÂªncias:** profundidade (unit apenas ou +E2E).

### C9 e2e-compra-completa

- **Objetivo:** jornada real: cadastro/login Ã¢ÂÂ endereÃÂ§o Ã¢ÂÂ catÃÂ¡logo Ã¢ÂÂ adicionar Ã¢ÂÂ carrinho Ã¢ÂÂ checkout PIX Ã¢ÂÂ pedidos Ã¢ÂÂ simular pagamento (Ã¢ÂÂ cancelamento, se C2 concluÃÂ­da).
- **Requisitos:** decisÃÂ£o registrada no `design` da change `validar-jornada-compra-e2e`.
- **Funcionalidades:** `e2e/tests/` novo; credenciais via `.env`; sem screenshots no Git.
- **ExcluÃÂ­do:** pagamentos reais, CI, secrets.
- **Regras:** E6; E5 (throttle 10 req/20 s); `workers=1`; nunca mutar catÃÂ¡logo semeado.
- **DependÃÂªncias:** C1, C2; infraestrutura `e2e/` existente; mediÃÂ§ÃÂ£o E5.
- **BLOQUEIO (E6):** exige **ambiente de testes isolado e autorizado**. Dados efÃÂªmeros e limpeza em instÃÂ¢ncia compartilhada **nÃÂ£o equivalem a isolamento**. Permanece bloqueada atÃÂ© existir soluÃÂ§ÃÂ£o aprovada (ex.: ambiente/instÃÂ¢ncia Xano dedicada de teste). NÃÂ£o iniciar sem essa aprovaÃÂ§ÃÂ£o.
- **Aceite:** jornada completa verde em ambiente isolado aprovado; nenhum dado real exposto; suÃÂ­te E2E estÃÂ¡vel.
- **PendÃÂªncias:** soluÃÂ§ÃÂ£o de isolamento aprovada; roteiro de cancelamento na jornada.
