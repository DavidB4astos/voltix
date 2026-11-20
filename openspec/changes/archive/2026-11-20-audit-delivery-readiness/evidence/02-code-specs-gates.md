# Evidência 02 — Código, specs e gates

Data: 20/11/2026  
Worktree: `.worktrees/audit-delivery-readiness` (branch `audit-delivery-readiness`, base `43156b2`)

## 1. Coerência entre documentação, OpenSpec e código

- **Arquitetura (`AGENTS.md` + `docs/project-overview.md` + `docs/domain-model.md`):**
  - Frontend em Reflex (`voltix/`), backend e dados em Xano/XanoScript (`xano/`), controle incremental via OpenSpec (`openspec/`).
  - Nenhuma tecnologia ou dependência fora do escopo aprovado foi introduzida.
- **Rotas registradas em `voltix/voltix.py` (linhas 11425–11473):**
  - Públicas / Cliente: `/`, `/catalogo`, `/cliente`, `/carrinho`, `/checkout`, `/pedidos`.
  - Internas: `/interno`, `/interno/recuperar-senha`, `/interno/redefinir-senha`.
  - Nota: o 404 observado em `/entrar` na frente `01-runtime` é **falso positivo**, pois a rota real da área do cliente é `/cliente`.
- **Cobertura documental:**
  - `28` capabilities consolidadas em `openspec/specs/`.
  - `27` arquivos de teste em `tests/test_*.py`.

## 2. Gates obrigatórios executados

| Gate | Comando | Resultado | Observação |
|---|---|---|---|
| Suíte completa (sandbox) | `python -m unittest discover -s tests -q` (com `PYTHONPATH` do `.venv`) | `443 OK`, `2` falhas de rede local em `test_public_catalog_http_recovery` | Bloqueio esperado de `localhost` dentro do sandbox |
| Recuperação HTTP local (fora do sandbox) | `python -m unittest tests.test_public_catalog_http_recovery -q` | `Ran 2 tests in 1.098s — OK` | Confirma 445/445 testes válidos |
| Compilação Reflex | `python -m reflex compile` + `git restore reflex.lock` | `Success: App compiled successfully in 32.343 seconds` (`exit 0`) | `reflex.lock/*` restaurado; `git status --short` sem ruído |
| Higiene de diff | `git diff --check` | `exit 0` (sem erros) | — |
| Validação OpenSpec | `openspec validate --all --strict` | `Totals: 29 passed, 0 failed (29 items)` | 28 specs + change `audit-delivery-readiness` |

> Nota de ambiente: o `.venv\Scripts\python.exe` da raiz aponta para o caminho de usuário anterior (`C:\Users\venda\...`), portanto os comandos Python/Reflex foram executados com `C:\Users\David Bastos\AppData\Local\Programs\Python\Python314\python.exe` usando `PYTHONPATH` apontando para `.venv\Lib\site-packages`, sem alterar `.venv` nem `requirements.txt`.
