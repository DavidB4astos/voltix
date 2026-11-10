# 02 — Publicação do PATCH interno de Cliente (10/11/2026)

## Dry-run restrito

```
xano workspace push -d xano --dry-run \
  -i "api/internal_customers/customer_id_PATCH.xs" \
  -i "api/internal_customers/api_group.xs"
```

Resultado:

```
Include: api/internal_customers/customer_id_PATCH.xs, api/internal_customers/api_group.xs
Matched: 2 of 114 files

API Endpoints        +1 created

CREATE           query              customers/{customer_id} PATCH
```

Nenhum schema, tabela, outro endpoint ou variável de ambiente apareceu no plano.

## Publicação (autorizada pelo usuário)

```
xano workspace push -d xano --force \
  -i "api/internal_customers/customer_id_PATCH.xs" \
  -i "api/internal_customers/api_group.xs"
```

Resultado:

```
Matched: 2 of 114 files
Synced 1 GUIDs to local files
Pushed 2 documents to workspace 147981 from xano in 1.6s
```

O CLI emitiu "Unresolved References" para as tabelas `user` e `CLIENTE`, o mesmo
comportamento heurístico de push parcial já observado nas changes anteriores.

## Verificação por pull independente

Pull completo para diretório temporário e inspeção do arquivo remoto:

```
Pulled 115 documents to <temporary directory>
```

Arquivo remoto equivalente: `api/voltix_internal_customers/customers/customer_id_PATCH.xs`.

Conferências:

- `db.get user` e `db.get CLIENTE` preservados, sem placeholders.
- `db.query CLIENTE` para unicidade de e-mail preservado.
- `db.patch CLIENTE` dentro de `db.transaction` preservado.
- `precondition` de `ADMINISTRADOR` ativo, validações de nome/e-mail/telefone/status
  e resposta mascarada preservadas.
- GUID local sincronizado: `0pBqUqLkVaUx9l5N8HX2sf2suzY`.

O pull normaliza apenas a formatação (linhas em branco e uma `precondition`
multilinha compactada); nenhuma referência virou placeholder e nenhuma regra foi
alterada.

## Limites

- Nenhuma chamada `PATCH` autenticada foi executada para não alterar dados reais.
- A verificação remota foi somente leitura (pull).
- A URL publicada deve ser configurada em `XANO_INTERNAL_CUSTOMER_UPDATE_URL`.
