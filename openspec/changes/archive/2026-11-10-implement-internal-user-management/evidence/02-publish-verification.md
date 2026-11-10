# Publicação e verificação remota — 10/11/2026

## Autorização

Publicação autorizada explicitamente pelo usuário após o dry-run mostrar apenas
`CREATE` para o grupo e os cinco endpoints.

## Dry-run

```text
xano workspace push -d xano --dry-run -i "api/internal_users/**"

API Groups           +1 created
API Endpoints        +5 created

CREATE  api_group  Voltix Internal Users
CREATE  query      profile/password POST
CREATE  query      profile PATCH
CREATE  query      users/{user_id} PATCH
CREATE  query      users GET
CREATE  query      users POST
```

## Publicação

```text
xano workspace push -d xano --force -i "api/internal_users/**"
Pushed 6 documents
```

Tentativas anteriores falharam por sintaxe do XanoScript (`db.edit` com `data`
variável e `db.patch` com `enforce_hidden_fields`) e sofreram rollback. A versão
final usa `db.edit` com objeto literal montado a partir dos valores atuais e dos
campos informados, preservando atualização parcial e campos protegidos.

## Pull independente

Pull em diretório temporário confirmou:

- grupo canônico `voltix-internal-users` e os cinco endpoints;
- `auth = "user"` e guards de perfil/status antes das leituras/escritas;
- allowlist `id`, `name`, `email`, `role`, `status`, `created_at` na listagem;
- ausência de `db.del user`;
- proteção do próprio perfil/status e do último administrador ativo;
- `security.check_password` na troca de senha;
- respostas sem senha, hash, token ou `password_reset`.

## Verificação remota somente leitura

Sem sessão, usando o caminho canônico `/api:voltix-internal-users/...`:

```text
GET    /users              -> 401
PATCH  /users/1            -> 401
PATCH  /profile            -> 401
POST   /users              -> 400 (campos obrigatórios ausentes, sem escrita)
POST   /profile/password   -> 400 (campos obrigatórios ausentes, sem escrita)
```

Nenhum registro real foi criado, alterado ou excluído.

## Limitação

O teste autenticado positivo (listar, criar, editar, inativar e trocar senha) não
foi executado; exige usuário sintético e autorização separada para escrita real.
