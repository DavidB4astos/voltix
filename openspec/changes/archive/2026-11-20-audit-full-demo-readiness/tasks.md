## 1. Preparação no worktree

- [x] 1.1 Criar worktree dedicado no Antigravity a partir de `79f57a5`, mudar a sessão para ele e
      confirmar `git status --short --branch` limpo com a change ativa listada por `openspec list` —
      verificação: worktree isolado em `HEAD (no branch)`, `main` limpo em `origin/main`, apenas esta
      change ativa (`0/24`)
- [x] 1.2 Criar a estrutura `evidence/` com `01-runtime.md`, `02-code-specs-gates.md`,
      `03-xano-readonly.md`, `04-security.md` e `05-demo-readiness.md`, reaproveitando o padrão da
      auditoria arquivada — verificação: 5 arquivos presentes, cada um com título, data 20/11/2026
      e seção `Limitações` reservada

## 2. Runtime e telas

- [x] 2.1 Inventariar rotas públicas e seções internas em 1280/768/375 px — verificação: 9 rotas × 3
      viewports = 27 combinações, todas com `overflow=0`, sem "Carregando" e sem badge; console sem
      `[error]`/`[warn]`, apenas avisos de `autocomplete`/`id` e um falso positivo `Connection Error:`
      vazio; registrado em `evidence/01-runtime.md`
- [x] 2.2 Navegar catálogo → detalhe → carrinho sem mutação — verificação: 20 produtos, preços
      `a partir de R$`, placeholder de imagem, painel de detalhe com SKU/estoque/ação e estado de
      carrinho sem sessão; botão de adicionar ao carrinho **não** acionado e nenhuma escrita na rede
- [x] 2.3 Navegar área ADMIN (Produtos e Pedidos) com sessão, sem inativar/excluir/avanzar status —
      verificação: sessão ADMINISTRADOR indisponível após o restart do Chrome; conferência de badges,
      ações e valores em uma linha mantida pelo baseline de 20/11 e por `fix-demo-blockers`; nenhuma
      mutação executada; limitação documentada em `evidence/01-runtime.md`
- [x] 2.4 Verificar o login de Cliente e documentar o 403 conhecido, sem reset de senha — verificação:
      formulários presentes e sem dados sensíveis no DOM; 403 histórico registrado como limitação, sem
      reenvio de `POST` e sem reset; próxima ação depende de autorização para credenciais de teste
- [x] 2.5 Mostrar checkout/pedido em estados existentes sem submeter compra — verificação: estados de
      "entre como Cliente" em `/checkout` e `/pedidos` conferidos no DOM; nenhuma requisição `POST` de
      pedido/pagamento registrada; jornada marcada como simulação em `evidence/01-runtime.md`

## 3. Código, specs e gates

- [x] 3.1 Suíte completa com `.venv-novo-pc\Scripts\python.exe -m unittest discover -s tests -q` —
      verificação: **Ran 445 tests ... OK**; `ResourceWarning` de HTTPError simulados no stderr não
      é falha de teste, conforme registrado em `evidence/02-code-specs-gates.md`
- [x] 3.2 `reflex compile` — verificação: sucesso em 23,584 s; `reflex.lock/bun.lock` e
      `reflex.lock/package.json` restaurados via `git restore --worktree`
- [x] 3.3 `git diff --check` — verificação: limpo, executado após a restauração do `reflex.lock/*`
- [x] 3.4 `openspec validate --all --strict` — verificação: 29 itens válidos (28 specs + a change
      ativa), 0 falhas; avisos informativos de requisitos longos registrados
- [x] 3.5 Conferir `docs/AI_AGENT_HANDOFF.md` e `docs/roadmap-changes.md` contra o commit `79f57a5` —
      verificação: changes ativas e Xano consistentes; uma inconsistência pós-entrega em
      `AI_AGENT_HANDOFF.md:631` (435 em vez de 445 testes) registrada para a tarefa 6.5

## 4. Xano somente leitura

- [x] 4.1 Comparar contratos locais e publicados sem `push`, `PATCH`, `POST` ou `DELETE` —
      verificação: pull de metadados (126 documentos) em diretório temporário, sem `--env`/`--records`;
      `preco_minimo` conferido nos dois lados; diferenças de serialização e tabela remota
      `tmp_rollback_test` listadas sem correção em `evidence/03-xano-readonly.md`
- [x] 4.2 Confirmar o endpoint público `products_GET` com `preco_minimo` e os 20 produtos ativos —
      verificação: uma chamada GET → HTTP 200, 20 itens, 20/20 com `preco_minimo`, sem HTTP 429 e sem
      exposição de dados pessoais
- [x] 4.3 Registrar pendências históricas (joins de carrinho/checkout, defaults de schema, upload e
      tabela remota temporária) — verificação: cinco itens listados em `evidence/03-xano-readonly.md`,
      sem nova publicação e sem remoção da tabela temporária

## 5. Segurança e autorização

- [x] 5.1 Revisar papéis e guardas em código e XanoScript — verificação: matriz de 5 papéis montada em
      `evidence/04-security.md`, coerente com E1/E2/E4, specs consolidadas e roadmap; dois falsos
      positivos, uma pendência pós-entrega (superfície legada) e provas autenticadas como limitação
- [x] 5.2 Verificar ausência de CPF, e-mail, telefone, senha, hash, token e `.env` no DOM e nas
      evidências — verificação: 9 rotas varridas com 0 CPF/e-mail/telefone/token/config; campos de senha
      apenas em formulários de auth; 5 arquivos de evidência limpos, conforme `evidence/04-security.md`
- [x] 5.3 Confirmar negação de acesso anônimo e inativo nas rotas internas — verificação: cinco GETs
      anônimos espaçados → HTTP **401** em todos, sem 429 e sem escrita; negação de inativo mantida
      como limitação documentada por exigir credencial e POST de login

## 6. Consolidação e fechamento

- [x] 6.1 Preencher matriz achado → jornada → classificação (bloqueador de demo, pós-entrega,
      limitação documentada, falso positivo) → próxima ação — verificação: 12 linhas em
      `evidence/05-demo-readiness.md`, com veredito "sem bloqueador de demo no escopo executável"
- [x] 6.2 Escrever o roteiro de ensaio das quatro jornadas com limitações explícitas — verificação:
      `evidence/05-demo-readiness.md` contém passos, telas esperadas e a lista do que não deve ser
      executado (compra, mutação, reset, publicação, dados sensíveis)
- [x] 6.3 Revisão final dos gates e do working tree — verificação: `git diff --check` limpo,
      `reflex.lock/*` restaurado, `openspec validate --all --strict` com 29 passed/0 failed, único item
      não rastreado é a própria change; 20/24 tarefas concluídas antes do fechamento
- [x] 6.4 Arquivar a change com `openspec archive audit-full-demo-readiness -y --skip-specs` —
      verificação: diretório `archive/2026-11-20-audit-full-demo-readiness`, nenhuma change ativa,
      `skip_specs` respeitado e `openspec validate --all --strict` com 28 passed/0 failed
- [x] 6.5 Atualizar `docs/AI_AGENT_HANDOFF.md` e `docs/roadmap-changes.md` — verificação: item 17 no
      handoff, nova seção no roadmap, contagem de testes corrigida de 435 para 445 e links para as
      cinco evidências arquivadas; nenhuma spec consolidada alterada
- [x] 6.6 Commit/push somente com autorização explícita — verificação: autorização do usuário obtida
      em 20/11/2026 para trazer os artefatos à `main`, commitar e pushar; nenhum commit/push foi feito
      antes desta autorização
