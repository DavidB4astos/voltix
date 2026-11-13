# Verificação — 13/11/2026

## Problema

Os endpoints `POST /users` (criação de UsuarioInterno por ADMINISTRADOR) e
`POST /profile/password` (troca de senha própria) eram publicados com
`text password filters=min:8|minAlpha:1|minDigit:1` e
`text new_password filters=min:8|minAlpha:1|minDigit:1`. Inputs `text` do Xano não
aceitam `minAlpha`/`minDigit` (somente colunas/inputs `password`, que hasham o valor
no bind); o servidor rejeitava **toda** chamada com `ERROR_CODE_INPUT_ERROR`,
deixando criação de usuário e troca de senha indisponíveis em produção.

## Correção

Os dois endpoints passaram a `filters=min:8` com precondition de letra e dígito via
`regex_test`. Assertions estáticas em `tests/test_internal_user_management.py`
cobrem ausência dos filtros inválidos, presença do `regex_test` e a ordem
autorização → validação → escrita. Nenhuma tabela, rota, contrato de resposta ou
regra de autorização foi alterado.

## Verificação local antes da publicação

```text
openspec validate fix-internal-users-password-filters --strict
Change 'fix-internal-users-password-filters' is valid

git diff --check
sem erros (apenas avisos de normalização LF/CRLF)

xano workspace push -d xano --dry-run -i "api/internal_users/users_POST.xs" -i "api/internal_users/profile/password_POST.xs"
API Endpoints  ~2 updated (users POST, profile/password POST)
```

## Publicação

Autorizada explicitamente pelo usuário em 13/11/2026.

```text
xano workspace push -d xano --force -i "api/internal_users/users_POST.xs" -i "api/internal_users/profile/password_POST.xs"
Pushed 2 documents
```

## Pull independente

Pull em diretório temporário confirmou os dois endpoints e normalização esperada do
importador: `regex_test` → `regex_matches` (e `query "x"` → `query x`, como na
change anterior). Nenhuma divergência adicional; demais endpoints do grupo intactos
(o push foi restrito aos 2 documentos).

## Verificação remota somente leitura

Sem sessão, contra a instância de produção:

```text
POST /users                    -> 400 ERROR_CODE_INPUT_ERROR (Missing param: name)
POST /profile/password         -> 400 ERROR_CODE_INPUT_ERROR (Missing param: current_password)
POST /users (senha curta abc)  -> 400 ERROR_CODE_INPUT_ERROR (Input does not meet minimum length requirement of 8 characters; param=password)
POST /profile/password (new_password=abc) -> 400 ERROR_CODE_INPUT_ERROR (Input does not meet minimum length requirement of 8 characters; param=new_password)
```

Nenhuma escrita ocorreu. A verificação autenticada de ponta a ponta (usuário
descartável passando na regra e token carregado) não foi executada; exige sessão
autenticável autorizada e segue como limitação registrada — o mesmo padrão aceito nas
changes `implement-internal-user-management` e `implement-internal-password-recovery`.

## Limitações

- A guarda `auth = "user"` só pode ser exercitada end-to-end com credenciais válidas
  de usuário interno descartável (não executada aqui; o 403 de 13/11 no teste
  autenticado confirma negação de credenciais inválidas).
- `.env` local e `xano.lock` não foram alterados; `reflex.lock/*` permanece
  restaurado.
