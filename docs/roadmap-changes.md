# Roadmap de changes — Voltix

Atualizado em 30/10/2026 por conferência do repositório local. Fontes: [AGENTS](../AGENTS.md), [visão geral](project-overview.md), [domínio](domain-model.md), [configuração OpenSpec](../openspec/config.yaml), specs consolidadas, arquivos, manifesto e histórico Git. O histórico anterior permanece no Git.

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
| Estoque C1 | Adiado/bloqueado; checkout valida disponibilidade, mas não baixa nem reserva estoque. | Spec `checkout-orders`; [README do adiamento](deferred-changes/2026-10-23-baixa-estoque-checkout/README.md) |
| Consulta interna de clientes C4 | Concluída: leitura para Funcionário/Administrador, filtros, paginação, máscaras e detalhe. Acesso de Cliente e interno inativo negado; teste de ID coincidente aprovado. | [Revisão final](../openspec/changes/archive/2026-10-29-consulta-clientes-painel/evidence/final-review.md) |
| CRM, cancelamento e gestão operacional | Consulta C4 entregue. Histórico, atendimentos, cancelamento e gestão de pedidos continuam planejados, sem entrega completa dessas capabilities. | C2, C3, C6, C7 e C10 |
| E2E existente | Spec cobre login e navegação com leituras; não confirma compra nem simula pagamento. | `openspec/specs/e2e-playwright/spec.md` |

Os lotes de fotos até ASUS estão nos commits `18e7919`, `d215ce8`, `b4dfb46`, `ef0b6c7`, `f41ef3f` e `064e66b`; a pesquisa sem foto nova é `1f29f3b`. Preservam arquivos originais, fontes, licenças, avisos e evidências. Cinco pendentes: G203 LIGHTSYNC, M90, WD SN580 1TB, Ryzen 5 5600 e Archer C6. Não usar modelos parecidos, imagens geradas por IA para SKU ou conteúdo sem direitos demonstrados.

**C4 concluída e arquivada:** [consulta-clientes-painel](../openspec/changes/archive/2026-10-29-consulta-clientes-painel/proposal.md). Spec internal-customers consolidada após publicação restrita, validação autenticada e restauração da conta fictícia usada no teste de status. Limites das verificações registrados na revisão final. Concluída e arquivada em 30/10/2026: [refine-internal-workspace](../openspec/changes/archive/2026-10-30-refine-internal-workspace/evidence/final-review.md), shell desktop e navegação por perfil verificados como Administrador e Funcionário. Consulta e detalhe de Clientes refinados e arquivados em 30/10/2026: [refine-internal-customers-desktop](../openspec/changes/archive/2026-10-30-refine-internal-customers-desktop/evidence/final-review.md), com QA visual isolada e contratos/handlers preservados. Gestão de Produtos refinada e arquivada em 30/10/2026: [refine-internal-products-desktop](../openspec/changes/archive/2026-10-30-refine-internal-products-desktop/evidence/final-review.md), com formulários rotulados, tabela de variações e QA isolada sem mutações reais. Próxima etapa visual sugerida: Categorias e marcas. Histórico e atendimentos de CRM seguem como capabilities próprias. Consultar `openspec list` para o estado corrente.

## Decisões aprovadas E1–E7

| ID | Decisão preservada |
|---|---|
| E1 | Cancelamento por cliente e ADMINISTRADOR até PAGAMENTO_CONFIRMADO; depois apenas ADMINISTRADOR, respeitando estados válidos e consistência de pagamento/estoque. É decisão para C2, não recurso já disponível. |
| E2 | FUNCIONARIO pode consultar pedidos/clientes e registrar atendimentos. Alterações sensíveis exclusivas do ADMINISTRADOR. Autorização no backend. |
| E3 | Dashboard de vendas obrigatório, com faturamento e quantidade de pedidos (C10). |
| E4 | CPF mascarado por padrão; nunca expor senhas, hashes ou tokens. |
| E5 | Medir capacidade/consumo real no dashboard Xano antes de C7 e C9; reconfirmar limites aplicáveis. |
| E6 | Compra E2E com mutações somente em ambiente de testes isolado e autorizado. Não presumir que uma branch isola dados; dados efêmeros com limpeza em instância compartilhada não equivalem a isolamento. |
| E7 | Testes focados por change; E2E apenas quando necessário. |

## Limites e bloqueios técnicos

O roadmap anterior registrou Xano Free com 10 requisições/20 s, 100.000 registros, um workspace, ausência de ambientes isolados e APIs/funções sujeitas a rate limit. Esses números são **registro histórico**, não verificação atual do plano ou do consumo. Esta change não consultou o dashboard nem alterou o serviço.

- C1 foi adiada por `db.direct_query` indisponível (`ERROR_CODE_ACCESS_DENIED`); não há alternativa comprovada de baixa atômica/rollback conjunto nesta revisão. Não escolher `db.patch` ou SQL como solução garantida sem prova técnica.
- Upload de imagem principal teve HTTP 403 no plano usado; não declarar funcional sem validação específica ou decidir armazenamento alternativo nesta change.
- Medir consumo de registros e histórico de 429 no dashboard, em leitura, antes de C7/C9.
- Reflex continua frontend, Xano/XanoScript continuam backend/dados; nenhuma nova plataforma aprovada por este roadmap.

## Matriz de autorização planejada

Esta matriz preserva E1/E2/E4 e o planejamento anterior; **não declara que endpoints futuros já existem**. Catálogo público também permite visitantes sem login. Recursos próprios usam sessão Cliente e propriedade derivada no backend. Acesso interno exige sessão, perfil e status ativos.

| Operação | CLIENTE | FUNCIONARIO | ADMINISTRADOR |
|---|---|---|---|
| Catálogo público e busca | Sim | Sim | Sim |
| Carrinho, checkout, endereços e pedidos próprios | Sim | Não por sessão interna | Não por sessão interna |
| Cancelar até PAGAMENTO_CONFIRMADO (C2) | Próprio | Não | Sim |
| Cancelar depois de PAGAMENTO_CONFIRMADO (C2) | Não | Não | Sim, estados válidos |
| Listar/ver todos os pedidos (C3) | Não | Sim | Sim |
| Transições de pedido (C3) | Não | Detalhar em design | Sim |
| Consultar clientes, CPF mascarado (C4) | Não | Sim | Sim |
| Registrar/editar atendimento aberto/em atendimento (C7) | Não | Sim | Sim |
| Finalizar/cancelar atendimento (C7) | Não | Detalhar em design | Sim |
| Dashboard de vendas (C10) | Não | Detalhar em design | Sim |
| Gestão de produtos/categorias/marcas | Não | Não | Sim; limitação de upload preservada |

O rascunho `consulta-clientes-admin` restringe a ADMINISTRADOR e diverge de E2; corrigir o contrato antes de retomar. Não publicar o draft nem interpretar suas tarefas antigas como concluídas.

## Ordem recomendada para propostas futuras

1. C4 concluída e arquivada em 29/10/2026. Consulta de clientes somente leitura entregue; o rascunho admin-only adiado foi preservado como referência histórica e não publicado.
2. Avaliar viabilidade de C1 no plano gratuito em proposta específica. Se não houver solução comprovada, manter bloqueada; não implementar baixa insegura.
3. Resolvida C1: C2 → C3 → C10, preservando ordem estoque, devolução, transições e agregados.
4. Resolvidas consultas C4/C3: C6 → C7, medindo capacidade antes de criar atendimentos.
5. C8 conforme lacunas reais e C9 somente com isolamento aprovado. Não duplicar as suítes existentes nem repetir testes sem motivo.

C5 já está concluída; não é próxima prioridade. As fotos restantes podem ser fornecidas como conteúdo em uma change específica quando houver modelo e direitos confirmados. Nenhum item desta sequência é autorização para execução.

## Escopo e aceite das propostas C1–C10

| ID / proposta | Escopo, dependências e critérios preservados |
|---|---|
| C1 baixa-estoque-checkout | Adiada, 0/11 no registro de adiamento. Baixar estoque na confirmação com atomicidade multi-item, rollback e estoque nunca negativo; carrinho não reserva. Concorrência da última unidade deve ser testada. Sem cancelamento, reserva ou tabela de movimentação. Preservar contrato vigente; proposta adiada usa HTTP 200, confirmado=false para indisponibilidade, não o 400 contraditório do roadmap antigo. Retomar apenas com solução Free comprovada e nova aprovação. |
| C2 cancelamento-pedido | Depende de C1. Cliente/ADMIN conforme E1; devolução apenas de unidades já baixadas, idempotente; histórico e pagamento 1:1 preservados. Testar pedido alheio, estado inválido e cancelamento repetido. Definir efeito no status do pagamento e confirmação de UI. Sem reembolso real, logística ou novo painel. |
| C3 gestao-pedidos-painel | Depende de C1/C2 no planejamento aprovado. Listar/detalhar pedidos e transições EM_PREPARACAO/ENVIADO/ENTREGUE; cancelamento reutiliza C2. Definir permissão do FUNCIONARIO, validar transições e autorização negativa no backend. Sem transportadora, CRM ou métricas. |
| C4 consulta-clientes-painel | Leitura de lista/detalhe; depende da autenticação interna existente. Compatibilizar o rascunho adiado com E2 e schema real. Definir campos, máscara, filtros combinados, paginação/limites e detalhe. Nunca senha/hash/token, CPF mascarado; negar anônimo/cliente/interno inativo. Testar vazio, erro e 429. Sem editar/inativar cliente, exportar, histórico ou atendimento. |
| C5 pesquisa-catalogo | Concluída e arquivada. Reutiliza products_GET com q por nome, filtro de categoria, cache e UI; correções futuras exigem nova justificativa, sem recriar capability. |
| C6 crm-cliente-historico | Depende de C4/C3. Cliente → pedidos, itens, valores e status, reutilizando consultas existentes; manter propriedade, histórico, consistência e CPF mascarado. Definir filtros por período/status e volume Free. Sem atendimentos, edição de cliente ou métricas. |
| C7 crm-atendimentos | Depende de C4/C6 e medição E5. Atendimento sempre vinculado a Cliente e UsuarioInterno; Pedido opcional do mesmo Cliente. ABERTO/EM_ATENDIMENTO atualizáveis, FINALIZADO/CANCELADO imutáveis. Definir quem finaliza e provisionamento inicial interno. Testar vínculos inválidos, imutabilidade e autorização. Sem mensagens, SLA ou automação. |
| C8 cobertura-testes-qualidade | Reavaliar lacunas antes de criar testes; não existem arquivos dedicados test_internal_access.py/test_integration_health.py no inventário desta revisão, o que não prova ausência total de cobertura indireta. Preservar objetivo de cobrir specs, sem duplicação ou teste que espelhe implementação. Originalmente posterior a C1–C7; focar behavior aprovado e suíte aplicável sem regressões. Sem nova feature ou axe-core automaticamente. |
| C9 e2e-compra-completa | Bloqueada por E6; depende de C1/C2 e ambiente isolado aprovado. Jornada de cadastro/login/endereço/catálogo/carrinho/checkout/pedidos/pagamento simulado, cancelamento se disponível. workers=1 e throttle conforme limites reconfirmados; nunca mutar catálogo real. Segredos por ambiente, não Git; sem pagamentos reais ou CI novo. Diferente da navegação de leitura existente. Evidências devem excluir dados pessoais e credenciais. |
| C10 dashboard-vendas | Depende de C1/C2/C3 para estados consistentes. Faturamento e quantidade por período; leitura, sem dados sensíveis. Definir período padrão, estados incluídos e acesso FUNCIONARIO no design; não transformar definição preliminar em nova regra contábil. Fixtures com valores corretos e acesso cliente negado. Sem previsões, metas, gráficos avançados, exportação ou CRM. |

## Riscos e sobreposições

- Falha parcial não pode persistir pedido com baixa incompleta. Uma venda da última unidade não pode permitir estoque negativo.
- Cancelamento repetido não pode duplicar estoque; devolver apenas o que foi efetivamente baixado.
- C3 consome C2; C6 usa C4 e consultas de pedidos; C5 não cria outro grupo de catálogo. Evitar endpoints e regras duplicados.
- Cliente não acessa CRM interno. Autorizações são do backend, não somente da interface.
- Não recriar catálogo, sessões, endereços, carrinho, checkout, pedidos próprios, pagamento simulado ou gestão já existente.
- Dados reais de clientes nunca entram em fixtures, capturas ou relatórios versionados.

## Inventário de referência

Os nomes abaixo foram conferidos no repositório; os detalhes de escopo, aceite e limitações ficam nos respectivos artefatos. A presença de uma pasta não substitui a leitura das evidências.

### Specs consolidadas

- `catalog-management`
- `checkout-orders`
- `customer-access`
- `customer-addresses`
- `e2e-playwright`
- `internal-access`
- `order-payment`
- `product-bulk-import`
- `product-management`
- `public-catalog`
- `public-home`
- `reflex-xano-integration`
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
