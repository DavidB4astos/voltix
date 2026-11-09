## 1. Preparação

- [x] 1.1 Confirmar o escopo com o usuário (backend + spec, sem tela; `GET customers/{id}/orders`; itens inline; filtros de status/período; paginação 20/50) — verificação: decisão registrada
- [x] 1.2 Conferir `pedido`, `item_pedido`, `variacao_produto` e os padrões de auth/paginação de C3/C4 — verificação: leitura dos `*.xs` coerente com a delta

## 2. Implementação

- [x] 2.1 Criar `GET customers/{customer_id}/orders` com acesso FUNCIONARIO/ADMINISTRADOR ativo e `notfound` para Cliente inexistente — verificação: language server oficial sem erros
- [x] 2.2 Validar `status`, `from`/`to` (`YYYY-MM-DD`, UTC, inclusivos), `page` e `per_page` (1–50) — verificação: preconditions explícitas no código
- [x] 2.3 Retornar Pedidos ordenados por `data_pedido desc, id desc`, com paginação e totais — verificação: `db.query` com `paging` e `totals`
- [x] 2.4 Incluir itens inline com valores persistidos, usando consultas agrupadas por página (sem N+1) — verificação: três `db.query` no máximo por página
- [x] 2.5 Garantir `itens: []` para Pedido sem item e lista parcial/ausente — verificação: revisão do código
- [x] 2.6 Garantir somente leitura e ausência de dados pessoais do Cliente (apenas `cliente_id`) — verificação: `output` restrito e ausência de campos sensíveis

## 3. Verificação local

- [x] 3.1 `openspec validate implement-c6-customer-order-history --strict` — verificação: válido
- [x] 3.2 Suíte `python -m unittest discover -s tests -q` preservada — verificação: 188 aprovados
- [x] 3.3 `git diff --check` limpo — verificação: sem conflitos/whitespace
- [x] 3.4 Commit focado com a implementação — verificação: `git log --oneline -1`

## 4. Publicação restrita

- [ ] 4.1 Dry-run somente do arquivo novo — verificação: preview anexado à evidência
- [ ] 4.2 **GATE** — aguardar confirmação explícita do usuário antes de publicar — verificação: OK registrado
- [ ] 4.3 Pull independente pós-publicação — verificação: diff confere com o local

## 5. Verificação remota mínima

- [ ] 5.1 Checagem somente leitura (rota sem sessão → 401), sem executar consulta autenticada — verificação: evidência em `evidence/`

## 6. Encerramento

- [ ] 6.1 Arquivar a change e consolidar a capability `customer-order-history` — verificação: `openspec validate --all --strict`
- [ ] 6.2 Atualizar `docs/roadmap-changes.md` (C6 concluída, matriz de autorização) e `docs/AI_AGENT_HANDOFF.md` — verificação: consistente com a evidência
- [ ] 6.3 `git status --short --branch` limpo — verificação: nada pendente
- [ ] 6.4 Commit focado + push somente com autorização explícita — verificação: `git log --oneline -1`
