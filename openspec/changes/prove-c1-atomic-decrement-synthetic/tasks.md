## 1. Preparação e pacote sintético

- [x] 1.1 Confirmar por escrito com o usuário que a exceção a E6 (prova somente com dados sintéticos no workspace Voltix, sem snapshot prévio) segue autorizada antes de qualquer escrita — verificação: registro da confirmação na evidência da change
- [x] 1.2 Criar o XanoScript local do pacote de prova (`test_c1_estoque`, rotas `c1_prova_baixa_POST` e `c1_prova_estado_GET`, grupo `c1_prova_temp`) com prefixos `TEST_C1_*`/`c1_prova_*` — verificação: arquivos revisáveis no diff, `openspec validate prove-c1-atomic-decrement-synthetic --strict` sem erros
- [x] 1.3 Cadastrar registros sintéticos iniciais somente após publicação (itens A–E: SKUs `TEST-C1-OK`, `TEST-C1-SEM-ESTOQUE`, `TEST-C1-MULTI-*`, `TEST-C1-LIMITE`) — verificação: inserção via `xano workspace push --records` após autorização; `c1_prova/estado` conferiu os 5 registros


## 2. Dry-run e publicação restrita

- [x] 2.1 Executar dry-run do pacote e apresentar ao usuário a lista exata de documentos e rotas que seriam publicados — verificação: saída do dry-run anexada à evidência
- [x] 2.2 **GATE**: aguardar confirmação explícita do usuário para publicar (nenhuma flag `--force`/`--sync`/`--delete`/`--records`/`--env`/`--truncate`/`--no-transaction`) — verificação: OK do usuário registrado
- [x] 2.3 Publicar somente o pacote de prova — verificação: pull independente comparando apenas as rotas/tabelas pretendidas (conteúdo confere com o local; GUIDs sincronizados; rotas seed/reset ficaram inalcançáveis na borda Free — ver evidence/03)
- [x] 2.4 Criar os registros sintéticos iniciais e conferir estoque de partida — verificação: inserção via `xano workspace push --records` (UPSERT por id, dry-run conferido); `c1_prova/estado` retorna os 5 registros (LIMITE=1)

## 3. Execução dos casos sintéticos

- [x] 3.1 Caso A — estoque suficiente: baixa aplicada uma vez — verificação: estoque reduzido exatamente pela quantidade (OK 5→3)
- [x] 3.2 Caso B — estoque insuficiente item único: `confirmado=false`, zero linhas afetadas, estoque inalterado — verificação: leitura sintética após a chamada (SEM-ESTOQUE=0)
- [x] 3.3 Caso C — dois itens, segundo sem estoque: rollback completo — verificação: ambos os itens com estoque original após a falha (MULTI-A=1)
- [x] 3.4 Caso D — duas chamadas simultâneas na última unidade do mesmo SKU — verificação: exatamente uma resposta confirma; estoque final 0; nunca negativo
- [x] 3.5 Caso E — deadlock cross-item com ordem invertida em duas transações — verificação: comportamento observado e registrado (concorrência reversa sem deadlock; perdedora revertida; LIMITE=0), sem corrupção de estoque
- [x] 3.6 Registrar o comportamento real de `db.increment` (linhas afetadas vs erro) e a resposta HTTP com `confirmado=false` — verificação: evidência sanitizada em `evidence/04-run-results.md`

## 4. Limpeza e verificação do workspace

- [ ] 4.1 Desabilitar/remover as rotas de prova e, se permitido, a tabela `test_c1_estoque` (UI do Xano se o CLI não suportar remoção segura) — verificação: pull/GETs confirmam ausência ou inacessibilidade — PARCIAL: CLI não oferece remoção segura (sem `--sync`/`--delete`); rotas já inalcançáveis na borda (404); baseline sintética restaurada; remoção completa pendente na UI (ver evidence/05-cleanup.md)
- [x] 4.2 Verificar que nenhum SKU demo, Pedido, ItemPedido, cliente ou estoque real foi alterado — verificação: auditoria do histórico de pushes — somente artefatos sintéticos foram criados/alterados (evidence/05-cleanup.md)
- [x] 4.3 Excluir qualquer artefato sintético residual em `xano/` local que não deva ser versionado, ou registrá-lo se intencional — verificação: `xano/api/c1_prova_temp/` e `xano/table/test_c1_estoque.xs` removidos; `git status` só lista o diretório da change

## 5. Documentação e encerramento

- [x] 5.1 Atualizar `docs/roadmap-changes.md`, `docs/deferred-changes/2026-10-23-baixa-estoque-checkout/README.md` e `docs/AI_AGENT_HANDOFF.md` com a decisão E6 (exceção por dados fictícios) e o resultado GO/NO-GO da prova — verificação: arquivos consistentes com a evidência
- [x] 5.2 `openspec validate --all --strict` e `git status --short --branch` limpos/verificados — verificação: saída anexada (17 items passed)
- [x] 5.3 Commit focado com mensagem descritiva e, se houver autorização, push — verificação: `git log --oneline -1` → `cf98176`. Push **não** executado (sem autorização explícita); `main` está 1 commit à frente de `origin/main`.
