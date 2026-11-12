# Publicação e verificação remota — 12/11/2026

## Autorização

Publicação autorizada explicitamente pelo usuário em 12/11/2026 após o dry-run
mostrar apenas `CREATE` para o grupo e os dois endpoints.

## Dry-run

```text
xano workspace push -d xano --dry-run -i "api/internal_password_recovery/**"

API Groups           +1 created
API Endpoints        +2 created

CREATE  api_group  Voltix Internal Password Recovery
CREATE  query      confirm POST
CREATE  query      request POST
```

## Publicação

```text
xano workspace push -d xano --force -i "api/internal_password_recovery/**"
Pushed 3 documents
```

Os avisos sobre `table "user"` no import são esperados: a tabela não fazia parte do
include desta publicação e já existe no servidor.

## Pull independente

Pull em diretório temporário confirmou:

- grupo canônico `voltix-internal-password-recovery` (tags
  `voltix:internal-password-recovery`);
- endpoints públicos, sem `auth` e sem `security.create_auth_token`;
- guardas de `FUNCIONARIO`/`ADMINISTRADOR` ATIVO antes de qualquer leitura ou
  escrita;
- expiração `now + 3600` e flag `used`;
- respostas sem token, senha, hash ou `password_reset`.

A única normalização do round-trip foi a remoção das aspas de `query "request"` e
`query "confirm"` (forma canônica `query request` / `query confirm`); os arquivos
locais foram ajustados para ficar idênticos ao remoto.

## Correção descoberta na verificação remota

A primeira chamada a `POST confirm` retornou
`{"code":"ERROR_CODE_INPUT_ERROR","message":"Invalid method for filter - minAlpha"}`.
Inputs `text` do Xano não aceitam `minAlpha`/`minDigit` (existem apenas em colunas e
inputs `password`, que hasham o valor no bind e quebram as comparações). O endpoint
`confirm` passou a receber `password` como `text filters=min:8` e exige letra e
dígito na stack via `regex_test`, mantendo toda falha de confirmação com a mensagem
genérica. Republicado restritamente (`confirm_POST.xs`, `~1 updated`).

Os mesmos filtros inválidos existem em `internal_users` (`users_POST` e
`profile/password_POST`), publicados anteriormente; ficaram registrados para change
separada, por decisão do usuário em 12/11/2026.

## Verificação remota somente leitura

Usando o caminho canônico `/api:voltix-internal-password-recovery/...` e um e-mail
inexistente (`voltix-qa-nao-existe@example.com`), sem enviar e-mail e sem criar
nenhuma recuperação:

```text
request (e-mail inexistente)  -> 200 {"message":"Se o e-mail estiver cadastrado, enviaremos as instruções."}
request (e-mail inválido)     -> 400 ERROR_CODE_INPUT_ERROR
confirm (senha curta)         -> 400 (mínimo de 8 caracteres)
confirm (sem dígito)          -> 400 "Link inválido ou expirado."
confirm (confirmação difere)  -> 400 "Link inválido ou expirado."
confirm (conta inexistente)   -> 400 "Link inválido ou expirado."
```

Nenhum registro real foi criado, alterado ou excluído.

## Limitação

O teste autenticado positivo de ponta a ponta com e-mail não foi executado
(decisão explícita do usuário): a entrega real do e-mail não é comprovável no plano
Free e autenticar um usuário interno real exigiria criar token e alterar senha real.
