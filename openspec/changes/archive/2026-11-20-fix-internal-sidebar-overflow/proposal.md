## Why

Em capturas reais de `/interno` em viewport desktop com altura útil reduzida (~600 px), foram identificados dois problemas visuais em `assets/voltix-internal.css`:
1. **Transbordamento na base da sidebar**: `.vx-internal__sidebar` possui `height: 100vh` sem `overflow-y: auto` e com espaçamentos verticais altos (`padding: 34px 20px 24px`, `margin-bottom: 44px` na marca, `padding-top: 40px` no rodapé). Com os 9 itens de navegação, o bloco de identidade do usuário e o botão `Sair da conta` transbordam abaixo do fundo escuro `#071525`, ficando com texto claro sobre o fundo claro da página.
2. **Quebra de e-mail em `Meu perfil` → `Identidade`**: `.vx-profile__values` usa `minmax(140px, 1fr)` com `overflow-wrap: anywhere`, quebrando o endereço de e-mail no meio do domínio.

## What Changes

- **Sidebar interna (`assets/voltix-internal.css`):**
  - Adicionar `overflow-y: auto` em `.vx-internal__sidebar` para impedir qualquer vazamento visual para fora do fundo `#071525`.
  - Compactar o ritmo vertical da sidebar (`padding`, margens da marca/eyebrow/rodapé e `gap`/`padding` dos itens) para que todos os 9 links, `Ver loja`, o card do usuário e `Sair da conta` caibam confortavelmente em telas ~600 px sem precisar rolar.
- **Card `Identidade` em `Meu perfil` (`assets/voltix-internal.css`):**
  - Ajustar `.vx-profile__values` para `minmax(180px, 1fr)` e `overflow-wrap: break-word` em `.vx-profile__value dd` para evitar quebras no meio de domínios curtos.
- **Fora do escopo:** alterações em `State`, Xano, loja pública, mobile (`<=800px`) ou specs consolidadas.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- Nenhuma (`skip_specs: true` em `.openspec.yaml`).

## Impact

- **Worktree:** `.worktrees/fix-internal-sidebar-overflow` (branch `fix-internal-sidebar-overflow`).
- **Arquivos:** `assets/voltix-internal.css` e teste focado em `tests/`.
- **Gates:** `python -m unittest discover -s tests -q`, `reflex compile` (com restauração de `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`.
