## 1. Preparação

- [x] 1.1 Confirmar o escopo de publicação com o usuário (dois endpoints + função `CancelOrder`; nenhum é publicado sem dry-run e confirmação explícita) — verificação: escopo "Backend + spec" aprovado pelo usuário
- [x] 1.2 Conferir tabelas `pedido`, `item_pedido`, `variacao_produto`, `pagamento` e perfis `CLIENTE`/`user` para consistência com a spec — verificação: `Get-Content` de cada `*.xs` coerente com a delta

## 2. Implementação

- [x] 2.1 Criar função Xano `Voltix Orders/cancel_order` com os parâmetros (`order_id`, `kind`), precondições, transação e retorno padronizado — verificação: `xano/function/voltix_orders/cancel_order.xs` validado pelo language server oficial do XanoScript
- [x] 2.2 Criar query `customer/orders/{order_id}/cancel` (auth CLIENTE; `kind="cliente"`) — verificação: `xano/api/customer/order_id_cancel_POST.xs` com checagem de dono por `$auth.id`
- [x] 2.3 Criar query `internal/orders/{order_id}/cancel` (auth user; exige `ADMINISTRADOR`; `kind="admin"`) — verificação: `xano/api/internal_orders/order_id_cancel_POST.xs` com precondição de papel; `FUNCIONARIO` negado
- [x] 2.4 Garantir idempotência estrita e ausência de efeitos quando já `CANCELADO` — verificação: leitura de estado dentro da transação; `db.edit` não suporta `where` (confirmado no language server), risco concorrente registrado no design

## 3. Verificação local

- [x] 3.1 `openspec validate implement-c2-order-cancellation --strict` — verificação: válido
- [x] 3.2 Suíte `python -m unittest discover -s tests -q` preservada — verificação: 188 aprovados (exit 0)
- [x] 3.3 `git diff --check` limpo — verificação: sem conflitos/whitespace
- [x] 3.4 Commit focado com a implementação — verificação: `git log --oneline -1` → `968481c`

## 4. Publicação restrita

- [x] 4.1 Dry-run de `function/voltix_orders/cancel_order.xs`, `api/customer/order_id_cancel_POST.xs`, `api/internal_orders/api_group.xs` e `api/internal_orders/order_id_cancel_POST.xs` — verificação: preview em `evidence/01-dry-run-preview.md` (1 função, 1 grupo, 2 endpoints; sem avisos)
- [x] 4.2 **GATE** — aguardar confirmação explícita para publicar qualquer um dos três documentos; publicar somente os pacotes aprovados — verificação: OK do usuário registrado em 09/11/2026 ("Sim, publicar os 4 documentos"); push restrito executado
- [x] 4.3 Pull independente pós-publicação para cada um dos documentos publicados — verificação: `evidence/02-publish-verification.md`

## 5. Verificação remota mínima

- [x] 5.1 Execução somente de verificações aprovadas pelo usuário (leitura/estados esperados); nenhuma escrita em Pedido/ItemPedido/Pagamento/estoque real sem autorização e dados sintéticos+limpeza na UI — verificação: `evidence/02-publish-verification.md` (pull + 401 nas duas rotas)

## 6. Encerramento

- [ ] 6.1 Arquivar a delta spec como nova capability `order-cancellation` — verificação: `openspec validate --all --strict` sem conflitos
- [ ] 6.2 Atualizar `docs/roadmap-changes.md`, `docs/AI_AGENT_HANDOFF.md` e defer/decisions (E1) — verificação: consistente com a evidência
- [ ] 6.3 `git status --short --branch` limpo — verificação: nada pendente
- [ ] 6.4 Commit focado + push somente com autorização explícita do usuário — verificação: `git log --oneline -1`
