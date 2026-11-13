## 1. Correção

- [x] 1.1 Reescrever `_cart_money_text` em Python (string + pad de fração, sem
      `rx.Var`) — verificação: `R$ 119,90`, `R$ 119,00`, `R$ 119,50`, `R$ 0,00`
- [x] 1.2 Preservar assinatura e call sites (tipo `str | rx.Var[str]`) — verificação:
      `reflex compile` sem erros

## 2. Testes

- [x] 2.1 Criar `tests/test_money_display.py` cobrindo `119`, `119.5`, `119.90`, `0.00`, `'1234.50'`, strings com entrada inválida (exceção) — verificação:
      `.venv-novo-pc\Scripts\python.exe -m unittest tests.test_money_display -v` (5 OK)
- [x] 2.2 Rodar a suíte completa — verificação: `python -m unittest discover -s tests -q` (435 testes OK)
- [x] 2.3 `openspec validate fix-money-display --strict` — verificação: válido

## 3. Verificação visual e encerramento

- [x] 3.1 `reflex compile` — verificação: sucesso
- [x] 3.2 Servidor local e captura do Dashboard (e preços em Produtos) mostrando o formato novo sem aspas — verificação: avaliado no DOM via `querySelectorAll` — `["R$ 119,90","1","R$ 119,90"]` e lista de preços de variações sem aspas
- [x] 3.3 `openspec validate --all --strict` e `git diff --check` — verificação:
      30 itens válidos (29 com a change ativa + esta) e sem erros de whitespace
- [x] 3.4 Restaurar `reflex.lock/*`, sincronizar spec, arquivar a change e atualizar docs —
      verificação: diretório em `archive/2026-11-13-fix-money-display/`
- [ ] 3.5 Commit/push somente com autorização explícita — verificação: árvore limpa e
      sincronizada com `origin/main`
