## 1. Correção de layout em CSS

- [x] 1.1 Ajustar `.vx-internal__sidebar` e seus espaçamentos internos em `assets/voltix-internal.css` (incluindo `overflow-y: auto` e ritmo vertical compacto)
- [x] 1.2 Ajustar `.vx-profile__values` e `.vx-profile__value dd` em `assets/voltix-internal.css` para evitar quebra de e-mail no TLD

## 2. Verificação e encerramento

- [x] 2.1 Adicionar teste focado em `tests/` verificando as regras de contenção da sidebar e perfil em `assets/voltix-internal.css`
- [x] 2.2 Executar `python -m unittest discover -s tests -q`, `reflex compile` (restaurando `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`
- [x] 2.3 Registrar evidência em `evidence/verification.md`, arquivar com `openspec archive fix-internal-sidebar-overflow -y --skip-specs` e solicitar autorização antes de commit/push
