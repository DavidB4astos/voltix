# Roadmap de Changes — Voltix

Documento central de organização do desenvolvimento.

Fontes: `AGENTS.md`, `docs/project-overview.md`, `docs/domain-model.md`, `openspec/config.yaml`, specs consolidadas, changes ativas/arquivadas, auditoria documental, código atual Reflex e XanoScript.

## Regras

- Implementar **UMA change por vez**. Sem paralelismo nem intercalamento.
- Não recriar changes arquivadas nem funcionalidades já existentes.
- Toda change encerrada (spec + implementação + testes) antes de abrir a próxima.
- Decisões E1–E7 abaixo são **aprovadas e não são reabertas**.
- **A aprovação deste roadmap NÃO autoriza criar nem implementar changes futuras. Cada change exige aprovação individual antes de qualquer criação OpenSpec ou alteração de código/Xano.**

## Estado atual

- **ATIVA:** nenhuma. `cadastro-produtos-em-massa` foi **concluída (17/17 tarefas)**, **arquivada em 2026-10-18** (`openspec/changes/archive/2026-10-18-cadastro-produtos-em-massa/`) e **publicada em `origin/main`** (commits `d7ef848`, `39039cb`), com a spec consolidada criada em `openspec/specs/product-bulk-import/spec.md`. Antes disso, `gestao-produtos` foi **concluída (15/15 tarefas)**, **arquivada em 2026-10-18** (`openspec/changes/archive/2026-10-18-gestao-produtos/`) e **publicada em `origin/main`** (commits `3421dc8`, `3b91921`). **Limitação conhecida:** o upload de imagem principal (`POST /products/{id}/image`) não é operacional na instância Xano Free (HTTP 403, `ERROR_CODE_ACCESS_DENIED`) — permanece **não validado e não declarado funcional**, dependendo de plano pago ou armazenamento externo gratuito a tratar em mudança própria.
- **BLOQUEADA por limitação técnica (Xano Free):** `baixa-estoque-checkout` (C1) — artefatos OpenSpec criados; implementação bloqueada até confirmar que `db.direct_query` participa da transação/rollback do checkout.
- **ARQUIVADAS (17, concluídas, não recriar):** integracao-reflex-xano, acesso-interno, carrinho-compras, catalogo-publico, gestao-categorias-marcas, pagamento-pedido, design-interface-voltix, home-publica-voltix, resiliencia-catalogo-publico, cadastro-cliente-enderecos, checkout-pedidos, conectar-catalogo-publico-xano, documentacao-ap2, melhorar-ux-ui-ap2, validar-jornada-compra-e2e, gestao-produtos, cadastro-produtos-em-massa.

## Decisões aprovadas (E1–E7)

| # | Decisão |
|---|---|
| E1 | Cancelamento: cliente e `ADMINISTRADOR` até `PAGAMENTO_CONFIRMADO`; depois **apenas ADMINISTRADOR**, respeitando estados válidos e consistência pagamentos/estoque. |
| E2 | `FUNCIONARIO` pode consultar pedidos/clientes e registrar atendimentos. Alterações sensíveis são exclusivas do `ADMINISTRADOR`. Matriz de autorização no backend. |
| E3 | Dashboard de vendas obrigatório (faturamento + quantidade de pedidos) → change C10. |
| E4 | CPF mascarado por padrão. Nunca expor senhas, hashes ou tokens. |
| E5 | Limites Xano Free verificados (abaixo). Consumo real pendente de medição no dashboard. |
| E6 | Compra E2E com mutações **somente** em ambiente de testes isolado e autorizado. **Não presumir** que uma branch Xano isola os dados. |
| E7 | Testes focados por change; E2E somente quando necessário. |

## Limites Xano Free (E5, verificado)

| Item | Limite documentado |
|---|---|
| Requisições API | 10 req / 20 s (`ERROR_CODE_TOO_MANY_REQUESTS`) |
| Registros (Postgres) | 100.000 |
| Workspaces | 1 |
| Ambientes isolados | Não disponíveis (recurso pago) |
| APIs / funções | Ilimitadas (rate-limited) |

**Não verificável daqui:** consumo real de registros e histórico de rate limit. Medir no dashboard Xano (read-only) antes de **C7** e **C9** e registrar o resultado.

## Matriz de autorização

Padrão do repo: interno = `auth="user"` + `role`/`status`; cliente = `auth="CLIENTE"` + precondition `cliente_id == $auth.id`.

| Operação | CLIENTE | FUNCIONARIO | ADMINISTRADOR |
|---|---|---|---|
| Catálogo público e busca (C5) | ✔ | ✔ | ✔ |
| Carrinho, checkout, endereços, pedidos próprios | ✔ | ✖ | ✖ |
| Cancelar pedido ≤ `PAGAMENTO_CONFIRMADO` (E1) | ✔ | ✖ | ✔ |
| Cancelar pedido > `PAGAMENTO_CONFIRMADO` (E1) | ✖ | ✖ | ✔ |
| Listar/ver todos os pedidos (C3) | ✖ | ✔ | ✔ |
| Transição `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE` | ✖ | pendência C3 | ✔ |
| Listar/ver clientes, CPF mascarado (C4) | ✖ | ✔ | ✔ |
| Registrar/editar atendimento `ABERTO`/`EM_ATENDIMENTO` (C7) | ✖ | ✔ | ✔ |
| Finalizar/cancelar atendimento | ✖ | pendência C7 | ✔ |
| Dashboard de vendas, leitura (C10) | ✖ | pendência C10 | ✔ |
| CRUD produtos/categorias/marcas (já vigente); upload de imagem **indisponível no Xano Free** | ✖ | ✖ | ✔ |

Pendências são detalhadas no `design` da respectiva change na hora da implementação; não reabrem E2.

## Riscos técnicos registrados

1. **Atomicidade de estoque (C1):** baixa multi-step em `checkout_confirm`; falha no meio não pode deixar pedido persistido. Mitigação: pré-condição + `db.patch` guardado (`quantidade_disponivel >= q`) dentro da transação; rejeitar o pedido inteiro; teste de concorrência da última unidade.
2. **Cancelamento e devolução (C2):** devolução idempotente; duplo cancelamento não pode duplicar estoque; preservar pagamento 1:1 e histórico.
3. **Isolamento E2E (C9/E6):** sem ambiente Xano isolado no Free (1 workspace, sem ambientes isolados). **Dados efêmeros e limpeza em instância compartilhada não equivalem a isolamento** → ver bloqueio da C9. Complementar: rate limit 10 req/20 s exige `workers=1` e throttle.
4. **Consistência pedidos/pagamentos/estoque:** ordem obrigatória baixa (C1) → devolução (C2) → transições (C3) → agregados (C10). Nenhuma mudança de status sem regra de estoque resolvida.

## Ordem sequencial recomendada

```
F0  gestao-produtos (CONCLUÍDA 15/15, arquivada 2026-10-18)
F1  cadastro-produtos-em-massa (CONCLUÍDA 17/17, arquivada 2026-10-18)
 1  C1  baixa-estoque-checkout
 2  C2  cancelamento-pedido
 3  C3  gestao-pedidos-painel
 4  C10 dashboard-vendas
 5  C4  consulta-clientes-painel
 6  C5  pesquisa-catalogo          (zero dependências; pode subir para 1 se priorizado)
 7  C6  crm-cliente-historico
 8  C7  crm-atendimentos           ← exige medição E5 no dashboard
 9  C8  cobertura-testes-qualidade
10  C9  e2e-compra-completa        ← BLOQUEADO: ver item C9
```

## Sobreposições evitadas

- C2 fornece o endpoint/regra de cancelamento; C3 apenas o consome.
- C4 entrega a leitura de clientes; C6 reutiliza-a como porta de entrada.
- C3 e C6 reutilizam os endpoints de pedidos existentes.
- C5 estende `products_GET` existente; não cria novo grupo de API.
- Nada já existente deve ser recriado: catálogo público, auth interna, auth de cliente, endereços, carrinho, checkout, pedidos, pagamento simulado, gestão de produtos/categorias/marcas, UI de status e botões.

## Changes planejadas

Status: **C1 BLOQUEADA por limitação técnica (Xano Free)**; as demais permanecem **PLANEJADA**.

### C1 baixa-estoque-checkout

- **Status:** BLOQUEADA por limitação técnica (Xano Free) (proposta OpenSpec criada; implementação bloqueada pela tarefa 1).

- **Objetivo:** baixar `quantidade_disponivel` na confirmação do pedido.
- **Requisitos:** domínio 5.1/5.2/8.15/8.17; overview 6.1.
- **Funcionalidades:** baixa transacional; pré-condição de disponibilidade; contrato de resposta inalterado.
- **Excluído:** cancelamento, reserva, movimentação de estoque, painel.
- **Regras:** inteiro ≥ 0; 0 = indisponível mas ativo; falha = pedido inteiro negado; carrinho não reserva.
- **Dependências:** `checkout_confirm_POST.xs`; `test_checkout_orders.py`.
- **Aceite:** sem estoque → 400 e nada persistido; com estoque → baixa exata; **suíte aplicável completa aprovada, sem regressões**; teste de concorrência da última unidade.
- **Pendências:** formato do erro de indisponibilidade; log de baixa.

### C2 cancelamento-pedido

- **Objetivo:** cancelar pedido por cliente/ADMIN e devolver estoque (E1).
- **Requisitos:** domínio 5.3/8.17; overview 4.1/4.2.
- **Funcionalidades:** endpoint de cancel; regra de estados; devolução idempotente; UI em `/pedidos`.
- **Excluído:** painel de gestão, reembolso real, logística.
- **Regras:** E1; pagamento 1:1 preservado; histórico preservado; devolver somente se baixado (depende de C1).
- **Dependências:** C1 (obrigatória).
- **Aceite:** cancel em `AGUARDANDO_PAGAMENTO` devolve estoque exato; pós-`PAGAMENTO_CONFIRMADO` só ADMIN; estados inválidos rejeitados; cliente não cancela pedido alheio; duplo cancel idempotente; suíte completa sem regressões.
- **Pendências:** mensagem/UI de confirmação; efeito sobre status do `Pagamento`.

### C3 gestao-pedidos-painel

- **Objetivo:** listar/ver pedidos no painel e aplicar transições `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE`.
- **Requisitos:** overview 4.2/6.2; domínio 5.3.
- **Funcionalidades:** `GET /admin/orders`, `GET /admin/orders/{id}`, `PATCH /admin/orders/{id}/status`; UI no painel.
- **Excluído:** transportadora, métricas (C10), CRM.
- **Regras:** transições apenas no sentido válido; cancelamento via C2 (sem duplicar devolução); autorização no backend.
- **Dependências:** C1, C2.
- **Aceite:** FUNCIONARIO/ADMIN conforme matriz; transição inválida rejeitada; cliente negado; autorização negativa completa; suíte sem regressões.
- **Pendências:** permissão de transição para FUNCIONARIO (detalhar no design).

### C10 dashboard-vendas

- **Objetivo:** painel com faturamento e quantidade de pedidos (E3).
- **Requisitos:** overview 4.2 ("acompanhar informações relacionadas às vendas").
- **Funcionalidades:** agregados (total de pedidos, faturamento) por período; UI no painel; leitura apenas.
- **Excluído:** gráficos avançados, exportações, metas, previsão, CRM.
- **Regras:** faturamento = soma dos totais de pedidos não cancelados/não aguardando; sem dados sensíveis (E4).
- **Dependências:** C1, C2, C3 (statuses corretos).
- **Aceite:** valores corretos em fixtures; FUNCIONARIO conforme matriz; cliente negado; sem efeitos de estado; suíte sem regressões.
- **Pendências:** período padrão; quais statuses entram no faturamento (detalhar no design).

### C4 consulta-clientes-painel

- **Objetivo:** lista e detalhe de clientes no painel (somente leitura).
- **Requisitos:** overview 5.1/6.2; domínio 4.1.
- **Funcionalidades:** `GET /admin/customers`, `GET /admin/customers/{id}`; UI.
- **Excluído:** editar/inativar cliente, CRM, histórico (C6), exportação.
- **Regras:** CPF mascarado (E4); nunca senha/hash/token; cliente inativo preserva histórico.
- **Dependências:** padrão de auth interno existente.
- **Aceite:** FUNCIONARIO/ADMIN conforme matriz; cliente negado; payload sem credenciais; suíte sem regressões.
- **Pendências:** paginação; campos expostos.

### C5 pesquisa-catalogo

- **Objetivo:** busca textual por nome/descrição no catálogo público.
- **Requisitos:** overview 3/5.1/6.1.
- **Funcionalidades:** parâmetro `q` em `products_GET`; campo na UI; estado vazio; resiliência mantida.
- **Excluído:** fuzzy, ranking, autocomplete, IA, multi-imagem.
- **Regras:** somente produtos/variações `ATIVO`; endpoints via `.env`; rate limit/log mantidos.
- **Dependências:** nenhuma.
- **Aceite:** `test_public_catalog` ampliado; busca vazia = lista normal; sem regressão de resiliência.
- **Pendências:** busca inclui SKU de variação? (decidir no design).

### C6 crm-cliente-historico

- **Objetivo:** no painel, consultar cliente → pedidos, itens, valores, status.
- **Requisitos:** overview 3/4.2/6.3; domínio 4.1/5.3.
- **Funcionalidades:** consulta de pedidos por `cliente_id` (uso interno) + UI de CRM.
- **Excluído:** atendimentos (C7), edição de cliente, métricas.
- **Regras:** histórico preservado; acesso restrito; consistência e-commerce↔CRM.
- **Dependências:** C4, C3.
- **Aceite:** autorização negativa; dados corretos de itens/totais; CPF mascarado; suíte sem regressões.
- **Pendências:** volume de dados no Free; filtros por período/status.

### C7 crm-atendimentos

- **Objetivo:** criar a entidade e o fluxo de registro/consulta de atendimentos (domínio 6.1, regras 18/19/20).
- **Requisitos:** overview 3/4.2/6.3; domínio 19/20.
- **Funcionalidades:** tabela `atendimento`; CRUD com auth interna; UI de registro/histórico.
- **Excluído:** `InteracaoAtendimento`/mensagens, SLA, automações.
- **Regras:** sempre Cliente + UsuarioInterno; pedido opcional e do mesmo cliente; `ABERTO`/`EM_ATENDIMENTO` atualizáveis; `FINALIZADO`/`CANCELADO` imutáveis.
- **Dependências:** C4, C6; medição E5 no dashboard (tabela nova).
- **Aceite:** regras 18/19/20 verificadas; pedido de outro cliente rejeitado; atendimento finalizado imutável; autorização negativa; suíte sem regressões.
- **Pendências:** quem pode finalizar (FUNCIONARIO?); provisionamento do 1º usuário interno.

### C8 cobertura-testes-qualidade

- **Objetivo:** cobrir specs sem testes (`internal-access`, `reflex-xano-integration`).
- **Requisitos:** AGENTS seção 6.
- **Funcionalidades:** `test_internal_access.py`; `test_integration_health.py`; regressão final.
- **Excluído:** novas funcionalidades; axe-core (adiado).
- **Regras:** não duplicar suítes existentes; testar apenas comportamento especificado.
- **Dependências:** C1–C7 concluídas (validar o que já existir na época).
- **Aceite:** `unittest discover -s tests` verde; specs sem cobertura = 0.
- **Pendências:** profundidade (unit apenas ou +E2E).

### C9 e2e-compra-completa

- **Objetivo:** jornada real: cadastro/login → endereço → catálogo → adicionar → carrinho → checkout PIX → pedidos → simular pagamento (→ cancelamento, se C2 concluída).
- **Requisitos:** decisão registrada no `design` da change `validar-jornada-compra-e2e`.
- **Funcionalidades:** `e2e/tests/` novo; credenciais via `.env`; sem screenshots no Git.
- **Excluído:** pagamentos reais, CI, secrets.
- **Regras:** E6; E5 (throttle 10 req/20 s); `workers=1`; nunca mutar catálogo semeado.
- **Dependências:** C1, C2; infraestrutura `e2e/` existente; medição E5.
- **BLOQUEIO (E6):** exige **ambiente de testes isolado e autorizado**. Dados efêmeros e limpeza em instância compartilhada **não equivalem a isolamento**. Permanece bloqueada até existir solução aprovada (ex.: ambiente/instância Xano dedicada de teste). Não iniciar sem essa aprovação.
- **Aceite:** jornada completa verde em ambiente isolado aprovado; nenhum dado real exposto; suíte E2E estável.
- **Pendências:** solução de isolamento aprovada; roteiro de cancelamento na jornada.
