## Why

A auditoria de runtime e código identificou melhorias pontuais de UX e acessibilidade que não são bloqueadores, mas elevam o acabamento visual e semântico das telas sem alterar regras de negócio:
- Avisos de acessibilidade no console para campo sem `id`/`name` em `/catalogo` e inputs sem `autocomplete` em `/cliente`, `/interno`, `/interno/recuperar-senha` e `/interno/redefinir-senha`.
- Placeholder `"Imagem não disponível"` em card e detalhe de produto apenas textual, sem apoio visual discreto.
- Estado vazio do painel de Atendimentos (`/interno`) pouco orientativo para o operador.

## What Changes

- **Acessibilidade de formulários (Reflex):**
  - Garantir `id` e `name` explícitos no campo de busca/filtro de `/catalogo`.
  - Adicionar atributos `auto_complete` (`email`, `current-password`, `new-password`, `name`, `tel`) nos formulários de `/cliente`, `/interno`, `/interno/recuperar-senha` e `/interno/redefinir-senha`.
- **Polimento do placeholder de imagem no catálogo:**
  - Incluir ícone discreto (`rx.icon("image-off")` ou equivalente já usado pelo tema) acima do texto `"Imagem não disponível"`, preservando exatamente o texto exigido pelas specs.
- **Estado vazio de Atendimentos (`/interno`):**
  - Melhorar o bloco de estado vazio no painel de Atendimentos com mensagem clara e orientação para criar o primeiro registro, preservando handlers e contratos existentes.
- **Fora do escopo:**
  - Adição de novas fotos de produto (congeladas por fonte/direitos).
  - Refatoração mobile ampla (375 px) de tabelas administrativas.
  - Qualquer alteração em Xano, endpoints, `State` de negócio, autenticação ou specs consolidadas.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- Nenhuma (`skip_specs: true` em `.openspec.yaml`).

## Impact

- **Worktree:** `.worktrees/refine-ui-accessibility` (branch `refine-ui-accessibility`), mantendo `main` intacta.
- **Arquivos esperados:** apenas módulos de apresentação em `voltix/` e eventuais testes unitários focados em `tests/`.
- **Gates obrigatórios:** `python -m unittest discover -s tests -q`, `reflex compile` (com restauração de `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`.
