## 1. Acessibilidade de formulários

- [x] 1.1 Localizar o campo sem `id`/`name` em `/catalogo` (`voltix/voltix.py`) e adicionar `id` e `name` explícitos sem quebrar handlers existentes
- [x] 1.2 Adicionar `auto_complete` adequado nos inputs de `/cliente`, `/interno`, `/interno/recuperar-senha` e `/interno/redefinir-senha`

## 2. Polimento visual do placeholder e empty state

- [x] 2.1 Enriquecer o placeholder `"Imagem não disponível"` em card e detalhe de produto com ícone discreto mantendo o texto exato (já possuía `rx.icon("image", ...)` em ambos; preservado sem duplicação)
- [x] 2.2 Aprimorar o empty state da lista de Atendimentos em `voltix/voltix.py` com orientação clara ao operador

## 3. Verificação e encerramento

- [x] 3.1 Adicionar ou ajustar testes unitários focados em `tests/` cobrindo os novos atributos/componentes sem duplicar suítes existentes
- [x] 3.2 Executar `python -m unittest discover -s tests -q`, `reflex compile` (restaurando `reflex.lock/*`), `git diff --check` e `openspec validate --all --strict`
- [x] 3.3 Registrar evidência em `evidence/verification.md`, arquivar com `openspec archive refine-ui-accessibility-and-empty-states -y --skip-specs` e solicitar autorização antes de commit/push
