## Why
Pendências locais misturam histórico, configurações compartilháveis, artefatos gerados e um rascunho administrativo sem validação. Precisamos preservar o material e tornar explícito o estado de cada grupo antes de versionar.

## What Changes
- Separar diagnósticos locais por regras específicas no .gitignore, sem apagar arquivos.
- Versionar comandos e skills OpenSpec do OpenCode e configuração MCP sem credenciais.
- Recuperar skills e lockfiles versionados; preservar cópia local da migração não validada, conforme autorização do usuário.
- Versionar documentação histórica de changes adiadas e substituídas.
- Preservar a consulta administrativa como rascunho adiado, com revisão dos problemas e condições de retomada, fora dos diretórios de endpoints publicáveis.

## Capabilities
Nenhuma capacidade de produto adicionada ou modificada. Mudança exclusivamente de organização, ferramentas e documentação; skip_specs intencional.

## Impact
Sem alteração de UI, eventos, regras de negócio ou Xano publicado. Não concluir nem arquivar como implementadas as changes adiadas. Enviar apenas commits revisados, mantendo credenciais, dependências instaladas e referências locais fora do Git.
