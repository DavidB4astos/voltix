## 1. Preparação

- [x] 1.1 Confirmar o escopo com o usuário (backend + spec, sem tela; transição só de ADMINISTRADOR) — verificação: decisão registrada ("Backend + spec" e "Só ADMINISTRADOR transiciona")
- [x] 1.2 Conferir `pedido`, `item_pedido`, `variacao_produto`, `pagamento`, `CLIENTE` e `user` e o padrão de paginação/máscara de `internal_customers` — verificação: leitura dos `*.xs` coerente com a delta

## 2. Implementação

- [x] 2.1 Criar `GET orders` com filtros `q`/`status`, paginação 1–50, ordenação estável e nome do Cliente — verificação: `xano/api/internal_orders/orders_GET.xs` validado pelo language server oficial (o filtro `|count` não existe no parser; a condição usa `cliente_id in $customer_ids` sem guarda de contagem)
- [x] 2.2 Criar `GET orders/{order_id}` com Cliente (e-mail mascarado), itens, endereço e Pagamento, sem dados sensíveis — verificação: `xano/api/internal_orders/order_id_GET.xs` validado; sem CPF/telefone/senha/token
- [x] 2.3 Criar `POST orders/{order_id}/status` com sequência estrita, no-op idempotente e `ADMINISTRADOR` apenas — verificação: `xano/api/internal_orders/order_id_status_POST.xs` validado; enum de entrada aceita só `EM_PREPARACAO`/`ENVIADO`/`ENTREGUE`
- [x] 2.4 Garantir que nenhuma transição altera estoque, itens, valores, endereço ou Pagamento — verificação: `db.edit` grava apenas `status`/`updated_at`

## 3. Verificação local

- [x] 3.1 `openspec validate implement-c3-internal-order-management --strict` — verificação: válido
- [x] 3.2 Suíte `python -m unittest discover -s tests -q` preservada — verificação: 188 aprovados (exit 0)
- [x] 3.3 `git diff --check` limpo — verificação: `git diff --cached --check` exit 0 (apenas warnings CRLF)
- [x] 3.4 Commit focado com a implementação — verificação: `git log --oneline -1` → `20c195f`

## 4. Publicação restrita

- [x] 4.1 Dry-run somente dos três arquivos novos — verificação: `evidence/01-dry-run-preview.md` (3 endpoints, nada fora do escopo)
- [ ] 4.2 **GATE** — aguardar confirmação explícita do usuário antes de publicar — verificação: OK registrado
- [ ] 4.3 Pull independente pós-publicação dos três documentos — verificação: diff confere com o local

## 5. Verificação remota mínima

- [ ] 5.1 Checagens somente leitura (rotas sem sessão → 401; papéis negados se houver credencial), sem escrita em Pedido/estoque real — verificação: evidência em `evidence/`

## 6. Encerramento

- [ ] 6.1 Arquivar a change e consolidar a capability `order-management` — verificação: `openspec validate --all --strict`
- [ ] 6.2 Atualizar `docs/roadmap-changes.md` (C3 concluída, matriz de autorização) e `docs/AI_AGENT_HANDOFF.md` — verificação: consistente com a evidência
- [ ] 6.3 `git status --short --branch` limpo — verificação: nada pendente
- [ ] 6.4 Commit focado + push somente com autorização explícita — verificação: `git log --oneline -1`
