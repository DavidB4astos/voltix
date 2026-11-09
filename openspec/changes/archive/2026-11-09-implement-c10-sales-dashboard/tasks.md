## 1. Preparação

- [x] 1.1 Confirmar o escopo com o usuário (backend + spec, sem tela; FUNCIONARIO e ADMINISTRADOR; status pagos/confirmados; últimos 30 dias) — verificação: decisão registrada
- [x] 1.2 Conferir `pedido` (campos `data_pedido`, `status`, `valor_total`) e o padrão de autenticação interna de C3/C4 — verificação: leitura dos `*.xs` coerente com a delta

## 2. Implementação

- [x] 2.1 Criar `GET reports/sales` com acesso FUNCIONARIO/ADMINISTRADOR ativo, período padrão de 30 dias e validação de `from`/`to` — verificação: language server oficial sem erros
- [x] 2.2 Calcular faturamento, quantidade, ticket médio e série diária apenas com os quatro status aprovados — verificação: regra explícita no código e em `status_incluidos`
- [x] 2.3 Garantir resposta zerada para período vazio, limites inclusivos e arredondamento em duas casas — verificação: revisão do cálculo
- [x] 2.4 Atualizar a descrição do grupo `Voltix Internal Orders` para o uso real por FUNCIONARIO/ADMINISTRADOR — verificação: diff de `api_group.xs`
- [x] 2.5 Garantir que a consulta é somente leitura e não expõe dados de Cliente — verificação: `output` restrito e ausência de `db.get CLIENTE`

## 3. Verificação local

- [x] 3.1 `openspec validate implement-c10-sales-dashboard --strict` — verificação: válido
- [x] 3.2 Suíte `python -m unittest discover -s tests -q` preservada — verificação: 188 aprovados
- [x] 3.3 `git diff --check` limpo — verificação: sem conflitos/whitespace
- [x] 3.4 Commit focado com a implementação — verificação: `git log --oneline -1`

## 4. Publicação restrita

- [x] 4.1 Dry-run somente dos dois arquivos (`reports_sales_GET.xs` e `api_group.xs`) — verificação: preview anexado à evidência
- [x] 4.2 **GATE** — aguardar confirmação explícita do usuário antes de publicar — verificação: OK registrado
- [x] 4.3 Pull independente pós-publicação dos dois documentos — verificação: diff confere com o local

## 5. Verificação remota mínima

- [x] 5.1 Checagem somente leitura (rota sem sessão → 401), sem executar agregação com dados reais — verificação: evidência em `evidence/`

## 6. Encerramento

- [x] 6.1 Arquivar a change e consolidar a capability `sales-dashboard` — verificação: `openspec validate --all --strict`
- [x] 6.2 Atualizar `docs/roadmap-changes.md` (C10 concluída, matriz de autorização) e `docs/AI_AGENT_HANDOFF.md` — verificação: consistente com a evidência
- [x] 6.3 `git status --short --branch` limpo — verificação: nada pendente
- [x] 6.4 Commit focado + push somente com autorização explícita — verificação: `git log --oneline -1`
