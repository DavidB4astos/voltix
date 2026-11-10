# Roadmap de changes — Voltix

Atualizado em 03/11/2026 por conferência do repositório local. Fontes: [AGENTS](../AGENTS.md), [visão geral](project-overview.md), [domínio](domain-model.md), [configuração OpenSpec](../openspec/config.yaml), specs consolidadas, arquivos, manifesto e histórico Git. O histórico anterior permanece no Git.

## Regras

- Uma change por vez, sem paralelismo ou intercalamento. Concluir e verificar antes de iniciar outra.
- Não recriar funcionalidades existentes nem changes arquivadas. Artefatos adiados ficam em `docs/deferred-changes/`, com bloqueio e condição de retomada; não são entregas concluídas.
- A aprovação deste roadmap não autoriza criar ou implementar changes futuras. Cada nova change exige aprovação individual antes de criar artefatos OpenSpec ou alterar código/Xano.
- Preservar as decisões E1–E7. Planejamento não equivale a implementação, publicação ou teste remoto.
- Arquivamento registra o encerramento do escopo daquela change; não comprova execução de toda a plataforma em produção.

## Estado atual e evidências

| Área | Situação em 29/10/2026 | Fonte |
|---|---|---|
| Catálogo público e pesquisa C5 | Implementados e arquivados. Busca por nome, combinável com categoria, já existe; não reabrir como funcionalidade nova. | `openspec/specs/public-catalog/spec.md`; `2026-10-23-pesquisa-catalogo`; `2026-10-27-public-catalog-search-ui` |
| Regressões de catálogo | Change antiga encerrada com auditoria e evidências. | `2026-10-29-corrigir-regressoes-catalogo`, commit `36e7923` |
| Home, cartões, detalhe e rodapé | Refinamentos desktop arquivados; histórico detalhado no inventário abaixo. Prioridade desktop preservada; não declarar auditoria mobile completa. | Specs `public-home`, `public-catalog`, `visual-interface` |
| Conta, carrinho, checkout e pedidos do cliente | Refinamentos desktop arquivados. Conferências com dados isolados não comprovam compra real completa. | `2026-10-28-refine-desktop-account/cart/checkout/orders`; specs correspondentes |
| Imagens locais dos produtos demo | 15 fotos aprovadas de 20, cinco pendentes. Infraestrutura existente; pendência atual é de conteúdo e direitos/modelo. | `assets/demo/manifest.json`; lotes Icecat e pesquisa arquivados em 29/10 |
| Gestão de produtos e importação em massa | Changes arquivadas. Upload de imagem no Xano Free permanece com limitação histórica documentada, não declarado operacional nesta revisão. | Specs `product-management`, `product-bulk-import` |
| Estoque C1 | **Implementada e publicada em 05/11/2026** (change `implement-c1-atomic-decrement`). Checkout baixa estoque atomicamente com guarda `db.increment` na mesma transação; rollback multi-item verificado em prova e refletido na spec consolidada. Verificação remota somente leitura. | Spec `checkout-orders`; [README do adiamento](deferred-changes/2026-10-23-baixa-estoque-checkout/README.md); [evidência da prova](../openspec/changes/archive/2026-11-05-prove-c1-atomic-decrement-synthetic/evidence/04-run-results.md); [evidência da publicação](../openspec/changes/archive/2026-11-05-implement-c1-atomic-decrement/evidence/01-publish-verification.md) |
| Cancelamento C2 | **Implementado e publicado em 09/11/2026** (change `implement-c2-order-cancellation`). Cliente cancela o próprio Pedido em `AGUARDANDO_PAGAMENTO`; ADMINISTRADOR cancela em `AGUARDANDO_PAGAMENTO` e `PAGAMENTO_CONFIRMADO`. Devolução de estoque, Pedido e Pagamento `CANCELADO` na mesma transação; repetição é idempotente. Verificação remota somente leitura. | Spec `order-cancellation`; [evidência](../openspec/changes/archive/2026-11-09-implement-c2-order-cancellation/evidence/02-publish-verification.md) |
| Consulta interna de clientes C4 | Concluída: leitura para Funcionário/Administrador, filtros, paginação, máscaras e detalhe. Acesso de Cliente e interno inativo negado; teste de ID coincidente aprovado. | [Revisão final](../openspec/changes/archive/2026-10-29-consulta-clientes-painel/evidence/final-review.md) |
| CRM, cancelamento e gestão operacional | Cancelamento C2, consulta/transição de pedidos C3 (backend + tela), histórico do Cliente C6 (backend + tela), relatório de vendas C10 (backend + tela) e atendimentos C7 (backend + tela) entregues em 09/11/2026. Restam C8 e C9. | C8, C9 |
| E2E existente | Spec cobre login e navegação com leituras; não confirma compra nem simula pagamento. | `openspec/specs/e2e-playwright/spec.md` |

Os lotes de fotos até ASUS estão nos commits `18e7919`, `d215ce8`, `b4dfb46`, `ef0b6c7`, `f41ef3f` e `064e66b`; a pesquisa sem foto nova é `1f29f3b`. Preservam arquivos originais, fontes, licenças, avisos e evidências. Cinco pendentes: G203 LIGHTSYNC, M90, WD SN580 1TB, Ryzen 5 5600 e Archer C6. Não usar modelos parecidos, imagens geradas por IA para SKU ou conteúdo sem direitos demonstrados.

**C4 concluída e arquivada:** [consulta-clientes-painel](../openspec/changes/archive/2026-10-29-consulta-clientes-painel/proposal.md). Spec internal-customers consolidada após publicação restrita, validação autenticada e restauração da conta fictícia usada no teste de status. Limites das verificações registrados na revisão final. Concluída e arquivada em 30/10/2026: [refine-internal-workspace](../openspec/changes/archive/2026-10-30-refine-internal-workspace/evidence/final-review.md), shell desktop e navegação por perfil verificados como Administrador e Funcionário. Consulta e detalhe de Clientes refinados e arquivados em 30/10/2026: [refine-internal-customers-desktop](../openspec/changes/archive/2026-10-30-refine-internal-customers-desktop/evidence/final-review.md), com QA visual isolada e contratos/handlers preservados. Gestão de Produtos refinada e arquivada em 30/10/2026: [refine-internal-products-desktop](../openspec/changes/archive/2026-10-30-refine-internal-products-desktop/evidence/final-review.md), com formulários rotulados, tabela de variações e QA isolada sem mutações reais. Próxima etapa visual sugerida: Categorias e marcas. A tela de histórico do Cliente foi entregue em [implement-customer-history-panel](../openspec/changes/archive/2026-11-09-implement-customer-history-panel/proposal.md); atendimentos de CRM foram entregues no backend (C7) e sua tela em [implement-attendance-panel](../openspec/changes/archive/2026-11-09-implement-attendance-panel/proposal.md); a tela de Pedidos (C3) foi entregue em `implement-order-panel`; a tela do Dashboard (C10) foi entregue em `implement-sales-dashboard-panel`. Consultar `openspec list` para o estado corrente.

## Prioridade após auditoria de sincronização — 30/10/2026

A [auditoria somente leitura do Xano](auditorias/xano-sync-2026-10-30.md) identificou divergências entre local e publicado. O achado crítico das quatro rotas legadas de clientes foi corrigido em [harden-published-legacy-customers](../openspec/changes/archive/2026-10-30-harden-published-legacy-customers/evidence/published-review.md), publicada e arquivada em 30/10/2026: quatro queries conferidas no novo pull e oito negativas HTTP 401, sem alterar registros reais ou outros documentos. O cadastro POST e a edição própria foram preservados; testes autenticados positivos de edição não foram executados nesta correção. Os identificadores locais de Product Management e Public Catalog foram alinhados aos grupos publicados em [reconcile-xano-group-identifiers](../openspec/changes/archive/2026-10-30-reconcile-xano-group-identifiers/evidence/final-review.md), sem mudar URLs ou publicar metadados no Xano. Diferenças editoriais de descrições/tags continuam explícitas. GETs administrativos de Produtos e Variações reconciliados e publicados em [reconcile-admin-product-reads](../openspec/changes/archive/2026-10-30-reconcile-admin-product-reads/evidence/published-review.md): allowlists, ordenação e erros de acesso, sem novas permissões ou mutações. Próxima área recomendada: contratos e ordenação do catálogo público; joins de carrinho/checkout, defaults e upload continuam pendentes. Ainda não declarar sincronização completa. Não fazer push global nem alterar/remover dados para fechar esse levantamento.
### Catálogo público reconciliado — 30/10/2026
A ordenação de categorias e variações foi publicada e verificada em [reconcile-public-catalog-ordering](../openspec/changes/archive/2026-10-30-reconcile-public-catalog-ordering/evidence/published-review.md). Somente duas queries alteradas; leituras públicas 200/404 verificadas, sem modificar registros. A listagem foi conferida, sem republicação. Esta etapa recomendada acima está concluída; próxima área candidata é a revisão dos joins/contratos de carrinho e checkout, antes de qualquer publicação. Defaults e upload também permanecem pendentes. Uma nova change requer escopo próprio e aprovação; não executar compras ou alterar estoque para auditar.

### Ordenação de carrinho e checkout reconciliada — 30/10/2026
Concluída a [reconcile-cart-checkout-ordering](../openspec/changes/archive/2026-10-30-reconcile-cart-checkout-ordering/evidence/published-review.md): quatro sort id asc em três rotas, publicação restrita conferida por pull e duas negativas GET cart 401. Nenhuma compra executada. A ausência de type inner no publicado não foi tratada como bug confirmado; falta prova isolada do comportamento dos joins. Essa pendência, defaults e upload continuam em revisão futura com escopo próprio; C1 segue adiada e nenhuma regra de estoque foi ampliada.

### Viabilidade de teste isolado dos joins — 30/10/2026
A avaliação documental [evaluate-isolated-cart-join-tests](../openspec/changes/archive/2026-10-30-evaluate-isolated-cart-join-tests/evidence/feasibility-review.md) foi concluída; a prova no runtime **não foi executada**. Perfil atual lista somente o workspace do Voltix, usuário não possui outro ambiente e sandbox automático é descrito oficialmente como pago. Mantida a gratuidade e E6. [Plano de retomada](deferred-changes/2026-10-30-cart-join-runtime-tests/README.md): somente em ambiente separado gratuito e autorizado; não modificar joins por suposição. Entregas independentes, como refinamento desktop de Categorias e marcas, podem ser propostas sem esperar esse teste.

### Categorias e marcas desktop — 30/10/2026
Concluída a [refine-internal-catalog-desktop](../openspec/changes/archive/2026-10-30-refine-internal-catalog-desktop/evidence/final-review.md): formulários rotulados, tabelas legíveis, ações específicas e estados preservados. 188 testes passaram e QA isolada verificou desktop 1440/1024, edição/cancelamento, loading/vazio/erro e exclusividade do Administrador. Sem alteração de State, handlers ou Xano; nenhuma mutação real executada. A sugestão visual anterior de Categorias e marcas foi atendida. Importação em massa pode ser avaliada como próxima tela, com escopo próprio; CRM histórico/atendimentos mantém dependências e bloqueios já documentados.

### Importação desktop — 30/10/2026
Concluída a [refine-internal-import-desktop](../openspec/changes/archive/2026-10-30-refine-internal-import-desktop/evidence/final-review.md): guia de arquivo, nome selecionado, prévia/relatório tabulares, confirmação explícita e bloqueio nativo do seletor durante processamento. 188 testes passaram; QA isolada verificou CSV fictício, linhas mistas/sem válidas, processamento/cancelamento, falhas, Funcionário e larguras 1440/1024. State, parsers, handlers, limites e Xano preservados. Nenhuma importação real executada. Shell interno, Clientes, Produtos, Categorias/marcas e Importação possuem refinamentos desktop próprios arquivados; novas capabilities de pedidos/CRM continuam sujeitas às dependências C1–C10.

## Decisões aprovadas E1–E7

| ID | Decisão preservada |
|---|---|
| E1 | Cancelamento por Cliente e ADMINISTRADOR enquanto o Pedido está em `AGUARDANDO_PAGAMENTO`; o ADMINISTRADOR estende para `PAGAMENTO_CONFIRMADO`. Implementado e publicado na C2 em 09/11/2026. As transições operacionais seguintes foram definidas e publicadas na C3 (`PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`, só ADMINISTRADOR). |
| E2 | FUNCIONARIO pode consultar pedidos/clientes e registrar atendimentos. Alterações sensíveis exclusivas do ADMINISTRADOR. Autorização no backend. |
| E3 | Dashboard de vendas obrigatório, com faturamento e quantidade de pedidos (C10). Backend entregue e publicado em 09/11/2026 via `GET reports/sales`; a tela do painel foi entregue em 09/11/2026 pela change `implement-sales-dashboard-panel`, sem backend novo. |
| E4 | CPF mascarado por padrão; nunca expor senhas, hashes ou tokens. |
| E5 | Medir capacidade/consumo real no dashboard Xano antes de C7 e C9; reconfirmar limites aplicáveis. C7: plano Free e 0 429 confirmados; consumo de registros não exposto pelo Xano (limitação registrada). C9 continua pendente. |
| E6 | Compra E2E com mutações somente em ambiente de testes isolado e autorizado. Não presumir que uma branch isola dados; dados efêmeros com limpeza em instância compartilhada não equivalem a isolamento. |
| E7 | Testes focados por change; E2E apenas quando necessário. |

## Limites e bloqueios técnicos

O roadmap anterior registrou Xano Free com 10 requisições/20 s, 100.000 registros, um workspace, ausência de ambientes isolados e APIs/funções sujeitas a rate limit. Esses números são **registro histórico**, não verificação atual do plano ou do consumo. Em 09/11/2026, a C7 confirmou o plano Free e 0 429, mas o Xano não exibiu o consumo de registros; a limitação está registrada na evidência da C7. Nenhum upgrade ou alteração de plano foi feito.

- C1: implementação concluída e publicada em 05/11/2026. O checkout baixa estoque atomicamente com guarda `db.increment` na mesma transação; rollback multi-item verificado na prova (04/11) e na spec consolidada. `db.direct_query` permanece indisponível (`ERROR_CODE_ACCESS_DENIED`).
- C2: implementação concluída e publicada em 09/11/2026. Cancelamento transacional com devolução de estoque e Pagamento `CANCELADO`; idempotente em série. Limite conhecido: `db.edit` não aceita `where`, então cancelamentos simultâneos no mesmo Pedido têm risco residual de devolução dupla (documentado no design).
- Upload de imagem principal teve HTTP 403 no plano usado; não declarar funcional sem validação específica ou decidir armazenamento alternativo nesta change.
- Medir consumo de registros e histórico de 429 no dashboard, em leitura, antes de C7/C9.
- Reflex continua frontend, Xano/XanoScript continuam backend/dados; nenhuma nova plataforma aprovada por este roadmap.

## Matriz de autorização planejada

Esta matriz preserva E1/E2/E4 e o planejamento anterior; **não declara que endpoints futuros já existem**. Catálogo público também permite visitantes sem login. Recursos próprios usam sessão Cliente e propriedade derivada no backend. Acesso interno exige sessão, perfil e status ativos.

| Operação | CLIENTE | FUNCIONARIO | ADMINISTRADOR |
|---|---|---|---|
| Catálogo público e busca | Sim | Sim | Sim |
| Carrinho, checkout, endereços e pedidos próprios | Sim | Não por sessão interna | Não por sessão interna |
| Cancelar em `AGUARDANDO_PAGAMENTO` (C2) | Próprio | Não | Sim |
| Cancelar em `PAGAMENTO_CONFIRMADO` (C2) | Não | Não | Sim |
| Cancelar em `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE` | Não | Não | Não |
| Listar/ver todos os pedidos (C3) | Não | Sim | Sim |
| Transições de pedido (C3) | Não | Não | Sim, sequência estrita |
| Consultar clientes, CPF mascarado (C4) | Não | Sim | Sim |
| Histórico de pedidos do Cliente (C6) | Não | Sim (leitura) | Sim |
| Registrar/editar atendimento aberto/em atendimento (C7) | Não | Sim | Sim |
| Iniciar atendimento `ABERTO → EM_ATENDIMENTO` (C7) | Não | Sim | Sim |
| Finalizar/cancelar atendimento (C7) | Não | Responsável | Sim; qualquer ADMINISTRADOR |
| Dashboard de vendas (C10) | Não | Sim (leitura) | Sim |
| Gestão de produtos/categorias/marcas | Não | Não | Sim; limitação de upload preservada |

O rascunho `consulta-clientes-admin` restringe a ADMINISTRADOR e diverge de E2; corrigir o contrato antes de retomar. Não publicar o draft nem interpretar suas tarefas antigas como concluídas.

## Ordem recomendada para propostas futuras

1. C4 concluída e arquivada em 29/10/2026. Consulta de clientes somente leitura entregue; o rascunho admin-only adiado foi preservado como referência histórica e não publicado.
2. C1 concluída e publicada em 05/11/2026; C2, C3, C6, C7 e C10 concluídas e publicadas em 09/11/2026, com telas de Atendimentos, Pedidos e Dashboard entregues. Próximo: concluir a revisão de qualidade da C8; a lacuna total de `internal-access` e `reflex-xano-integration` foi coberta em 10/11/2026.
3. Resolvidas C1, C2, C3, C6, C7 e C10; agregados de vendas preservam a ordem de transições da C3, o histórico reutiliza Cliente/Pedido e os atendimentos preservam vínculos e imutabilidade.
4. Resolvidas consultas C4/C3/C6 e atendimentos C7; as telas de Atendimentos, Pedidos e Dashboard foram entregues. Próxima entrega recomendada: C8.
5. C8 conforme lacunas reais (lacuna de `internal-access`/`reflex-xano-integration` coberta em 10/11/2026) e C9 somente com isolamento aprovado. Não duplicar as suítes existentes nem repetir testes sem motivo.

C5 já está concluída; não é próxima prioridade. As fotos restantes podem ser fornecidas como conteúdo em uma change específica quando houver modelo e direitos confirmados. Nenhum item desta sequência é autorização para execução.

## Escopo e aceite das propostas C1–C10

| ID / proposta | Escopo, dependências e critérios preservados |
|---|---|
| C1 baixa-estoque-checkout | **CONCLUÍDA (05/11/2026)**: prova de runtime em 04/11 + implementação publicada no XanoFree em 05/11 (change `implement-c1-atomic-decrement`). `db.increment` com guarda atômico em transação; rollback multi-item e concorrência verificados. Sem cancelamento, reserva ou tabela de movimentação. Restam C2, C3, C10. |
| C2 cancelamento-pedido | **CONCLUÍDA (09/11/2026)**: change `implement-c2-order-cancellation` publicada no XanoFree. Cliente cancela o próprio Pedido em `AGUARDANDO_PAGAMENTO`; ADMINISTRADOR em `AGUARDANDO_PAGAMENTO` e `PAGAMENTO_CONFIRMADO`. Devolução de estoque item a item, Pedido e Pagamento `CANCELADO` na mesma transação; repetição idempotente. Sem reembolso real, logística ou painel novo. C10, C6 e C7 foram concluídas em 09/11/2026. |
| C3 gestao-pedidos-painel | **CONCLUÍDA (09/11/2026)**: change `implement-c3-internal-order-management` publicada no XanoFree. `GET orders` (filtros `q`/`status`, paginação), `GET orders/{order_id}` (detalhe com e-mail mascarado) para FUNCIONARIO/ADMINISTRADOR ativos; `POST orders/{order_id}/status` só para ADMINISTRADOR, em sequência estrita `PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`, no-op idempotente. Sem tela no painel, transportadora, CRM ou métricas. Verificação remota somente leitura. |
| C4 consulta-clientes-painel | Leitura de lista/detalhe; depende da autenticação interna existente. Compatibilizar o rascunho adiado com E2 e schema real. Definir campos, máscara, filtros combinados, paginação/limites e detalhe. Nunca senha/hash/token, CPF mascarado; negar anônimo/cliente/interno inativo. Testar vazio, erro e 429. Sem editar/inativar cliente, exportar, histórico ou atendimento. |
| C5 pesquisa-catalogo | Concluída e arquivada. Reutiliza products_GET com q por nome, filtro de categoria, cache e UI; correções futuras exigem nova justificativa, sem recriar capability. |
| C6 crm-cliente-historico | **CONCLUÍDA (09/11/2026)**: change `implement-c6-customer-order-history` publicada no XanoFree. `GET customers/{customer_id}/orders` para FUNCIONARIO/ADMINISTRADOR ativos, somente leitura, com Pedidos do Cliente ordenados do mais recente ao mais antigo, itens inline com valores persistidos, filtros de status e período (`from`/`to` em UTC, inclusivos) e paginação 20/50. Tela entregue na change `implement-customer-history-panel` (09/11/2026), sem backend novo. Sem atendimentos, edição de cliente ou métricas. |
| C7 crm-atendimentos | **CONCLUÍDA (09/11/2026)**: change `implement-c7-attendance-management` publicada no XanoFree. Tabela `atendimento` e grupo `Voltix Internal CRM` com `POST atendimentos`, `GET atendimentos`, `GET atendimentos/{attendance_id}`, `PATCH atendimentos/{attendance_id}` e `POST atendimentos/{attendance_id}/status`, para FUNCIONARIO/ADMINISTRADOR ativos. Atendimento vinculado ao Cliente e ao responsável criador; Pedido opcional do mesmo Cliente. `ABERTO`/`EM_ATENDIMENTO` editáveis; `FINALIZADO`/`CANCELADO` imutáveis. `ABERTO → EM_ATENDIMENTO` por qualquer interno; finalizar/cancelar pelo responsável ou ADMINISTRADOR; mesmo status é no-op idempotente. Tela entregue na change `implement-attendance-panel` (09/11/2026), sem backend novo. Sem mensagens, SLA ou automação. |
| C8 cobertura-testes-qualidade | Reavaliar lacunas antes de criar testes; não existem arquivos dedicados test_internal_access.py/test_integration_health.py no inventário desta revisão, o que não prova ausência total de cobertura indireta. Preservar objetivo de cobrir specs, sem duplicação ou teste que espelhe implementação. Originalmente posterior a C1–C7; focar behavior aprovado e suíte aplicável sem regressões. Sem nova feature ou axe-core automaticamente. **Parcial em 10/11/2026**: change `add-internal-access-integration-tests` cobriu as lacunas totais de `internal-access` e `reflex-xano-integration` com 32 testes novos; as demais specs já possuem arquivos dedicados. Trabalho de qualidade remanescente exige novo escopo aprovado. |
| C9 e2e-compra-completa | Bloqueada por E6; depende de C1/C2 e ambiente isolado aprovado. Jornada de cadastro/login/endereço/catálogo/carrinho/checkout/pedidos/pagamento simulado, cancelamento se disponível. workers=1 e throttle conforme limites reconfirmados; nunca mutar catálogo real. Segredos por ambiente, não Git; sem pagamentos reais ou CI novo. Diferente da navegação de leitura existente. Evidências devem excluir dados pessoais e credenciais. |
| C10 dashboard-vendas | **CONCLUÍDA (09/11/2026)**: changes `implement-c10-sales-dashboard` (backend) e `implement-sales-dashboard-panel` (tela). `GET reports/sales` publicado no XanoFree para FUNCIONARIO/ADMINISTRADOR ativos, somente leitura, com faturamento, quantidade, ticket médio e série diária dos Pedidos em `PAGAMENTO_CONFIRMADO`/`EM_PREPARACAO`/`ENVIADO`/`ENTREGUE`; período padrão de 30 dias em UTC, `from`/`to` inclusivos e limite de 366 dias. Tela entregue sem backend novo, com filtros, cartões, série diária e estados de carregamento/vazio/erro. Sem previsões, metas, gráficos avançados, exportação ou CRM. Verificação remota somente leitura. |

## Riscos e sobreposições

- Falha parcial não pode persistir pedido com baixa incompleta. Uma venda da última unidade não pode permitir estoque negativo.
- Cancelamento repetido não pode duplicar estoque; devolver apenas o que foi efetivamente baixado.
- C3 consome C2; C6 usa C4 e consultas de pedidos; C7 usa C4/C6 e cria o grupo `internal-crm`; as telas de Atendimentos, Pedidos e Dashboard foram entregues sem backend novo. C5 não cria outro grupo de catálogo. Evitar endpoints e regras duplicados.
- Cliente não acessa CRM interno. Autorizações são do backend, não somente da interface.
- Não recriar catálogo, sessões, endereços, carrinho, checkout, pedidos próprios, pagamento simulado ou gestão já existente.
- Dados reais de clientes nunca entram em fixtures, capturas ou relatórios versionados.

## Inventário de referência

Os nomes abaixo foram conferidos no repositório; os detalhes de escopo, aceite e limitações ficam nos respectivos artefatos. A presença de uma pasta não substitui a leitura das evidências.

### Specs consolidadas

- `attendance-management`
- `catalog-management`
- `checkout-orders`
- `customer-access`
- `customer-addresses`
- `customer-history-panel`
- `customer-order-history`
- `e2e-playwright`
- `internal-access`
- `internal-customers`
- `internal-workspace`
- `order-cancellation`
- `order-management`
- `order-payment`
- `product-bulk-import`
- `product-management`
- `public-catalog`
- `public-home`
- `reflex-xano-integration`
- `sales-dashboard`
- `shopping-cart`
- `visual-interface`

### Changes arquivadas na conferência inicial

- `2026-09-23-integracao-reflex-xano`
- `2026-10-07-acesso-interno`
- `2026-10-07-carrinho-compras`
- `2026-10-07-catalogo-publico`
- `2026-10-07-gestao-categorias-marcas`
- `2026-10-07-pagamento-pedido`
- `2026-10-13-design-interface-voltix`
- `2026-10-13-home-publica-voltix`
- `2026-10-14-resiliencia-catalogo-publico`
- `2026-10-15-cadastro-cliente-enderecos`
- `2026-10-15-checkout-pedidos`
- `2026-10-15-conectar-catalogo-publico-xano`
- `2026-10-15-documentacao-ap2`
- `2026-10-15-melhorar-ux-ui-ap2`
- `2026-10-15-validar-jornada-compra-e2e`
- `2026-10-16-redesign-home-voltix`
- `2026-10-18-cadastro-produtos-em-massa`
- `2026-10-18-catalog-loading-state`
- `2026-10-18-gestao-produtos`
- `2026-10-19-imagens-reais-catalogo`
- `2026-10-23-pesquisa-catalogo`
- `2026-10-23-refine-storefront-home`
- `2026-10-27-organize-local-project-files`
- `2026-10-27-public-catalog-search-ui`
- `2026-10-27-refine-home-imagery`
- `2026-10-27-refine-home-visual`
- `2026-10-27-refine-public-catalog-cards`
- `2026-10-27-refine-public-footer`
- `2026-10-27-refine-public-product-details`
- `2026-10-28-add-verified-c920-photo`
- `2026-10-28-evaluate-open-icecat-images`
- `2026-10-28-import-icecat-hyperx-photo`
- `2026-10-28-polish-public-customer-entry`
- `2026-10-28-refine-desktop-account`
- `2026-10-28-refine-desktop-cart`
- `2026-10-28-refine-desktop-checkout`
- `2026-10-28-refine-desktop-orders`
- `2026-10-29-corrigir-regressoes-catalogo`
- `2026-10-29-import-icecat-asus-4060-photo`
- `2026-10-29-import-icecat-kingston-photos`
- `2026-10-29-import-icecat-monitor-photos`
- `2026-10-29-import-icecat-product-photos-batch-2`
- `2026-10-29-import-icecat-samsung-870-photo`
- `2026-10-29-research-remaining-product-photos`

### Artefatos adiados e preservados

- [Baixa de estoque](deferred-changes/2026-10-23-baixa-estoque-checkout/README.md).
- [Rascunho de consulta de clientes](deferred-changes/2026-10-27-consulta-clientes-admin/README.md).
- [Correção N+1 absorvida na Home](superseded-changes/2026-10-22-fix-catalog-image-n1/README.md): não recriar como change ativa.
- [Higiene do repositório](development/repository-hygiene.md).

### Defaults do endereço e Pedido — 03/11/2026
A change documental [audit-xano-schema-defaults](../openspec/changes/archive/2026-11-03-audit-xano-schema-defaults/evidence/verification.md) confirmou, por pull de metadados sem registros, que os schemas publicados não declaram os defaults locais `endereco.principal=false` e `pedido.valor_frete=0`. Os endpoints atuais informam ambos explicitamente, sem impacto observado. O fallback de inserções futuras que omitam os campos permanece não verificado; não publicar alteração nem afirmar sincronização completa com base nesta leitura.

### Contrato do upload de imagem — 04/11/2026
O trecho do endpoint publicado, copiado pelo usuário do Xano, confirma `file? image_file` opcional; o XanoScript local o declara obrigatório. O Reflex envia exatamente um arquivo com esse nome, e as guardas administrativas estão presentes. O endpoint não verifica explicitamente a presença do arquivo antes de usar `.name`; o efeito da ausência não foi testado. O HTTP 403 histórico é uma limitação separada do `storage.create_image` na instância Free, e upload atual continua sem validação operacional. Evidências: [endpoint publicado fornecido](../openspec/changes/archive/2026-11-03-evaluate-image-upload-contract/evidence/published-endpoint.md) e [revisão final](../openspec/changes/archive/2026-11-03-evaluate-image-upload-contract/evidence/final-review.md). Qualquer correção funcional ou teste remoto exige change própria aprovada.

### Prova de runtime da baixa atômica (C1) — 04/11/2026
Exceção documentada a E6 autorizada pelo usuário em 04/11/2026: prova executada exclusivamente com registros sintéticos (`TEST-C1-*`) na tabela `test_c1_estoque` do workspace `147981`, sem snapshot prévio (decisão explícita do usuário). `db.increment` com guarda (`quantidade_disponivel >= quantidade`, status ATIVO) dentro de `db.transaction` foi comprovado no runtime: decremento guardado atômico, rollback multi-item integral, disputa concorrente pela última unidade (1 vence, 1 recusada, estoque final 0) e concorrência reversa cross-item sem deadlock. HTTP 200 com `confirmado=false` preservado nos conflitos. Veredito: **GO para implementação da C1** como change própria (com delta na spec `checkout-orders`), ainda não aprovada. Limitações: sem carga/estresse; concorrência com 2 chamadas; workspace compartilhado. Artefatos de teste permanecem no Xano até exclusão na UI; rotas `c1_prova/*` estão inalcançáveis na borda Free (novos pushs não registram rotas via CLI). Evidência: [prove-c1-atomic-decrement-synthetic](../openspec/changes/prove-c1-atomic-decrement-synthetic/evidence/04-run-results.md).

### Implementação da baixa atômica (C1) — CONCLUÍDA E PUBLICADA — 05/11/2026
Change `implement-c1-atomic-decrement` implementada, publicada restritamente (somente `checkout_confirm_POST.xs`) e verificada no XanoFree. Pull confere; rota responde à validação esperada (400 `Missing param`); 188 testes e `openspec validate` verdes. Verificação remota = somente leitura (o usuário manteve essa decisão em 05/11/2026). Evidência: [01](../openspec/changes/implement-c1-atomic-decrement/evidence/01-publish-verification.md). Próximos: C2 → C3 → C10.

### Relatório de vendas (C10) — CONCLUÍDA E PUBLICADA — 09/11/2026
Change `implement-c10-sales-dashboard` implementada, publicada restritamente (`reports_sales_GET.xs` e `api_group.xs`) e verificada no XanoFree. `GET reports/sales` responde 401 sem sessão; pull independente confirma o endpoint e as referências `db.get user`/`db.query pedido`. Faturamento e quantidade somam apenas Pedidos em `PAGAMENTO_CONFIRMADO`, `EM_PREPARACAO`, `ENVIADO` ou `ENTREGUE`, com período padrão de 30 dias em UTC, `from`/`to` inclusivos e limite de 366 dias. 188 testes e `openspec validate --all --strict` verdes. A tela do painel fica para change própria. Evidência: [01](../openspec/changes/archive/2026-11-09-implement-c10-sales-dashboard/evidence/01-publish-verification.md).

### Histórico do Cliente (C6) — CONCLUÍDA E PUBLICADA — 09/11/2026
Change `implement-c6-customer-order-history` implementada, publicada restritamente (`customer_id_orders_GET.xs`) e verificada no XanoFree. `GET customers/{customer_id}/orders` responde 401 sem sessão; pull independente confirma o endpoint e as referências `db.get user`/`db.get CLIENTE`/`db.query pedido`/`db.query item_pedido`/`db.query variacao_produto`. Lista paginada (20/50) do Pedido mais recente ao mais antigo, com itens inline e valores persistidos, filtros de status e período UTC inclusivo, e acesso de FUNCIONARIO/ADMINISTRADOR ativos. 188 testes e `openspec validate --all --strict` verdes. Evidência: [01](../openspec/changes/archive/2026-11-09-implement-c6-customer-order-history/evidence/01-publish-verification.md).

### Atendimentos (C7) — CONCLUÍDA E PUBLICADA — 09/11/2026
Change `implement-c7-attendance-management` implementada, publicada restritamente (`table/atendimento.xs`, `api/internal_crm/api_group.xs` e cinco endpoints) e verificada no XanoFree. As rotas `GET /api:voltix-internal-crm/atendimentos` e `/atendimentos/1` respondem 401 sem sessão; pull independente confirma FKs para `CLIENTE`, `user` e `pedido`, `auth = "user"`, preconditions de FUNCIONARIO/ADMINISTRADOR ativo, enum de status, índices e regras de transição. A primeira verificação encontrou HTTP 400 por `filters=min:1` em campos opcionais; a correção foi publicada e as rotas passaram a responder 401. E5: plano Free e 0 429 confirmados; consumo de registros não exposto pelo Xano. 205 testes e `openspec validate --all --strict` verdes. Evidência: [04](../openspec/changes/archive/2026-11-09-implement-c7-attendance-management/evidence/04-publish-verification.md).

### Tela de histórico do Cliente — CONCLUÍDA — 09/11/2026
Change `implement-customer-history-panel` implementada sem backend novo. A ficha do Cliente ganhou uma seção de histórico em largura total, carregada automaticamente a partir de `GET customers/{customer_id}/orders`. Filtros de status e período (`from`/`to` em UTC, inclusivos), paginação de 20, Pedidos com resumo e itens sempre expandidos, estados de carregamento/vazio/erro e limpeza em logout/401/403. Contrato Python estrito valida a resposta antes do navegador; a nova variável `XANO_INTERNAL_CUSTOMER_ORDERS_URL` aponta para o endpoint já publicado. 205 testes, `openspec validate --all --strict` (21 itens) e `reflex compile` verdes. Evidência: [01](../openspec/changes/archive/2026-11-09-implement-customer-history-panel/evidence/01-local-verification.md).

### Tela de atendimentos (C7 UI) — CONCLUÍDA — 09/11/2026
Change `implement-attendance-panel` implementada sem backend novo. A seção **Atendimentos** foi liberada a FUNCIONARIO e ADMINISTRADOR ativos, com listagem filtrável por `cliente_id`/`status` e paginação de 20, criação com o interno autenticado como responsável, detalhe com vínculos somente leitura, edição apenas em `ABERTO`/`EM_ATENDIMENTO` e controles de status limitados por responsável/papel. O contrato `voltix/internal_attendances.py` valida chaves exatas, status, datas e totais; três variáveis server-side apontam para os endpoints C7 já publicados. `401` encerra a sessão; `403` em leitura/criação/edição também, enquanto `403` de transição é negação de operação e mantém a sessão. 235 testes, `openspec validate --all --strict` (23 itens), `git diff --check` e `reflex compile` verdes, com `reflex.lock` restaurado. Evidência: [01](../openspec/changes/archive/2026-11-09-implement-attendance-panel/evidence/01-local-verification.md).

### Tela de Pedidos (C3 UI) — CONCLUÍDA — 09/11/2026
Change `implement-order-panel` implementada sem backend novo. A seção **Pedidos** foi liberada a FUNCIONARIO e ADMINISTRADOR ativos, com busca por código/nome do Cliente, filtro de status, paginação de 20 e consumo de `GET orders`. O detalhe mostra Cliente e e-mail mascarado, itens, endereço, Pagamento e valores sem CPF/telefone/senha/hash/token. Apenas ADMINISTRADOR avança o status, um passo por vez (`PAGAMENTO_CONFIRMADO → EM_PREPARACAO → ENVIADO → ENTREGUE`), com repetição idempotente e transições inválidas bloqueadas localmente e no backend. O contrato `voltix/internal_orders.py` valida chaves exatas, status, datas, totais e máscara; três variáveis server-side apontam para os endpoints C3 já publicados. `401` encerra a sessão; `403` em leitura também, enquanto `403`/`400` no avanço são negação de operação e mantêm a sessão e o Pedido. 266 testes, `openspec validate --all --strict` (24 itens), `git diff --check` e `reflex compile` verdes, com `reflex.lock` restaurado. Evidência: [01](../openspec/changes/archive/2026-11-09-implement-order-panel/evidence/01-local-verification.md).

### Dashboard de vendas (C10 UI) — CONCLUÍDA — 09/11/2026
Change `implement-sales-dashboard-panel` implementada sem backend novo. A seção **Dashboard** tornou-se a primeira opção da navegação interna, liberada a FUNCIONARIO e ADMINISTRADOR ativos, consumindo o `GET reports/sales` já publicado. Exibe cartões de faturamento, Pedidos e ticket médio, o período aplicado, os status incluídos e a série diária em ordem crescente, com filtros opcionais `from`/`to` em UTC (limite de 366 dias inclusivos) e estados de carregamento, vazio, erro e sessão não autorizada. O contrato `voltix/internal_sales.py` valida chaves exatas, período, status, série e coerência de totais, quantizando valores monetários em duas casas. `401`/`403` encerram a sessão; `400` informa período inválido e mantém a sessão; respostas malformadas não renderizam. Nova variável server-side `XANO_INTERNAL_SALES_URL`. 290 testes, `openspec validate --all --strict` (25 itens), `git diff --check` e `reflex compile` verdes, com `reflex.lock` restaurado. Evidência: [01](../openspec/changes/archive/2026-11-09-implement-sales-dashboard-panel/evidence/01-local-verification.md).
### Cobertura de acesso interno e integração (C8) — CONCLUÍDA — 10/11/2026
Change `add-internal-access-integration-tests` implementada sem alteração de produção. Foram adicionados `tests/test_internal_access.py` e `tests/test_integration_health.py`, cobrindo login interno, validação de identidade/sessão, acesso protegido, logout, troca de identidade, separação Cliente × UsuarioInterno e o contrato de saúde do Xano com estados de sucesso, configuração ausente, HTTP, rede, payload inválido e nova tentativa. Asserções estáticas confirmam as guardas de perfil/status e a ausência de credenciais nos XanoScripts. 32 testes novos, 322 na suíte completa, `openspec validate --all --strict` (26 itens) e `git diff --check` verdes, com `reflex.lock` restaurado. Evidência: [01](../openspec/changes/archive/2026-11-10-add-internal-access-integration-tests/evidence/01-local-verification.md).