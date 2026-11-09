## 1. Preparação

- [x] 1.1 Confirmar o escopo da tela (histórico no detalhe do Cliente, seção larga abaixo, itens sempre expandidos, filtros TODOS + período, paginação 20) — verificação: decisão registrada
- [x] 1.2 Conferir o contrato publicado da C6 e o padrão de URL/token do painel — verificação: `customer_id_orders_GET.xs` e `State` lidos

## 2. Contrato Python

- [x] 2.1 Adicionar `InternalOrderItem`, `InternalOrder`, `history_parameters` e `order_history_page` em `voltix/internal_customers.py` — verificação: dataclasses e funções importáveis
- [x] 2.2 Validar chaves exatas, ids, status, valores monetários, datas, totais e tamanho da página — verificação: testes do contrato
- [x] 2.3 Rejeitar `status` inválido, datas fora de `YYYY-MM-DD`, `from > to`, página inválida e `per_page` fora de 1–50 — verificação: testes de parâmetros

## 3. State e handlers

- [x] 3.1 Adicionar campos do histórico, filtros, paginação, mensagem e geração — verificação: `State` inicializa sem erro
- [x] 3.2 Carregar o histórico automaticamente ao abrir a ficha e limpar em fechar/trocar/atualizar/limpar — verificação: testes de geração e sessão
- [x] 3.3 Implementar aplicar/limpar filtros e paginação anterior/próxima — verificação: testes dos handlers
- [x] 3.4 Tratar carregamento, vazio, erro, 401/403 e resposta obsoleta — verificação: testes de erro e concorrência
- [x] 3.5 Garantir uso de `XANO_INTERNAL_CUSTOMER_ORDERS_URL` com placeholder `{customer_id}` e token interno — verificação: teste da URL e autorização

## 4. Interface

- [x] 4.1 Renderizar a seção full-width abaixo da lista/detalhe, somente quando há Cliente selecionado — verificação: revisão visual/estrutural
- [x] 4.2 Adicionar filtros de status e período, aplicar/limpar e mensagens de estado — verificação: componentes com rótulos e `aria_label`
- [x] 4.3 Renderizar cartões de Pedido com resumo, itens expandidos, valores persistidos e aviso de itens ausentes — verificação: revisão dos componentes
- [x] 4.4 Adicionar paginação acessível e estilos escopados em `assets/voltix-internal.css` — verificação: classes e foco visível

## 5. Configuração e testes

- [x] 5.1 Documentar `XANO_INTERNAL_CUSTOMER_ORDERS_URL` em `.env.example`; configurar o ambiente local sem expor valor em documentação — verificação: nome presente, valor fora de specs
- [x] 5.2 Adicionar testes do contrato e dos handlers — verificação: novos testes passam
- [x] 5.3 Rodar `python -m unittest discover -s tests -q` — verificação: suíte verde
- [x] 5.4 Rodar `openspec validate implement-customer-history-panel --strict` — verificação: válido
- [x] 5.5 Rodar `reflex compile` e restaurar `reflex.lock/*` se alterado — verificação: compile OK e lockfiles limpos

## 6. Encerramento

- [x] 6.1 Arquivar a change e consolidar as capabilities — verificação: `openspec validate --all --strict`
- [x] 6.2 Atualizar `docs/roadmap-changes.md` e `docs/AI_AGENT_HANDOFF.md` — verificação: consistente com a tela entregue
- [x] 6.3 `git status --short --branch` limpo — verificação: nada pendente
- [x] 6.4 Commit focado + push somente com autorização explícita — verificação: `git log --oneline -1`
