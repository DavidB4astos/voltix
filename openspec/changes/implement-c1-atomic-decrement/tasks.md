## 1. Preparação

- [ ] 1.1 Confirmar com o usuário o escopo da verificação remota após a publicação (somente leitura vs. ciclo sintético completo com limpeza na UI) — verificação: decisão registrada na evidência
- [x] 1.2 Conferir spec consolidada atual de `checkout-orders` e a delta desta change — verificação: `openspec show checkout-orders --type spec --no-scenarios` coerente com a delta

## 2. Implementação local

- [x] 2.1 Adicionar decremento guardado por item no `checkout_confirm_POST.xs`, dentro da transação, ANTES de criar o Pedido (`db.increment` com guarda `id == variacao_id && quantidade_disponivel >= quantidade && status == "ATIVO"`, `return = {type: "count"}`) — verificação: diff revisável
- [x] 2.2 Se algum decremento afetar 0 linhas, lançar erro com nome `EstoqueInsuficiente` — verificação: diff revisável (nome canônico do parser: `inputerror`; mapeamento para resposta aprovada por `$erro_estoque`, ver design e evidência)
- [x] 2.3 Envolver a transação em `try_catch`; somente `EstoqueInsuficiente` vira resposta `confirmado=false` (HTTP 200, mesmas chaves da resposta atual); demais erros propagam — verificação: diff revisável
- [x] 2.4 Garantir que o ordering dos itens permanece `id asc` em todos os pontos e que nenhum outro endpoint/arquivo foi alterado — verificação: diff focado

## 3. Verificação local

- [x] 3.1 `openspec validate implement-c1-atomic-decrement --strict` — verificação: válido
- [x] 3.2 Suíte existente preservada — verificação: `python -m unittest discover -s tests -q` → 188 aprovados
- [x] 3.3 `git diff --check` limpo — verificação: sem problemas de whitespace/conflitos (apenas warnings CRLF informativos)
- [x] 3.4 Commit focado com a implementação — verificação: `git log --oneline -1`

## 4. Publicação restrita

- [x] 4.1 Dry-run somente de `api/customer/checkout_confirm_POST.xs` — verificação: preview anexado à evidência (`UPDATE query checkout/confirm POST`, sem erros)
- [x] 4.2 **GATE** — aguardar confirmação explícita do usuário e publicar somente esse arquivo — verificação: OK registrado ("confirmo" em 05/11/2026); publicado com `--force` (terminal não-interativo)
- [x] 4.3 Pull independente pós-publicação comparando somente `checkout_confirm_POST.xs` — verificação: diff do pull confere com o local (`try_catch`, `db.increment variacao_produto`, `erro_estoque` presentes); rota responde validação esperada (400 `Missing param: endereco_id`) e `err`

## 5. Verificação remota mínima (conforme decisão 1.1)

- [ ] 5.1 Executar apenas a verificação aprovada pelo usuário no gate 4.2; registrar evidência sanitizada (nenhuma escrita em estoque/pedido real sem autorização) — verificação: evidência em `evidence/`

## 6. Encerramento

- [ ] 6.1 Sincronizar delta spec com a spec consolidada `checkout-orders` — verificação: `openspec validate --all --strict` sem conflitos
- [ ] 6.2 Atualizar `docs/roadmap-changes.md` (C1 concluída), `docs/deferred-changes/2026-10-23-baixa-estoque-checkout/README.md` (implementado) e `docs/AI_AGENT_HANDOFF.md` — verificação: consistente com a evidência
- [ ] 6.3 `openspec validate --all --strict`; `git status --short --branch` — verificação: limpo
- [ ] 6.4 Commit focado da spec sincronizada e docs; push somente com autorização explícita — verificação: `git log --oneline -1`
