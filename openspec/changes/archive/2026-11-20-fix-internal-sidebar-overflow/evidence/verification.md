# Evidência — Correção do transbordamento da sidebar interna

Data: 20/11/2026  
Worktree: `.worktrees/fix-internal-sidebar-overflow` (branch `fix-internal-sidebar-overflow`)

## 1. Alterações aplicadas

- [voltix-internal.css](file:///c:/Users/David%20Bastos/Downloads/PROJETO%20VOLTIX/PROJETO%20VOLTIX/voltix/.worktrees/fix-internal-sidebar-overflow/assets/voltix-internal.css):
  - `.vx-internal__sidebar`: adicionado `overflow-y:auto` e compactado o ritmo vertical (`padding:20px 16px 16px`, `.vx-internal__brand` `margin:0 12px 20px`, `.vx-internal__eyebrow` `margin:0 14px 10px`, `.vx-internal__nav` `gap:4px`, `.vx-internal__nav-item` `padding:8px 12px`, `.vx-internal__bottom` `padding-top:16px`, `.vx-internal__store` `padding:8px 14px`, `.vx-internal__identity` `margin-top:8px;padding:12px 8px`).
  - `.vx-profile__values` e `.vx-profile__value dd`: coluna mínima ampliada para `minmax(180px,1fr)` com `overflow-wrap:break-word`.
- [test_internal_sidebar_css.py](file:///c:/Users/David%20Bastos/Downloads/PROJETO%20VOLTIX/PROJETO%20VOLTIX/voltix/.worktrees/fix-internal-sidebar-overflow/tests/test_internal_sidebar_css.py): teste unitário verificando contenção da sidebar e regra de `Meu perfil`.

## 2. Gates executados

- `python -m unittest discover -s tests -q`: `449/449` OK.
- `python -m reflex compile` + `git restore reflex.lock`: compilado sem erros.
- `git diff --check` e `openspec validate --all --strict`: limpos após arquivamento com `--skip-specs`.
