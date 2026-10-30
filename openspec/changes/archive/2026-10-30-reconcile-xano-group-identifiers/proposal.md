## Why
A auditoria identificou canonical local divergente dos grupos Product Management e Public Catalog em uso. Um envio futuro desses metadados poderia trocar bases de URL ou confundir a identidade dos grupos.
## What Changes
Alinhar somente canonical e GUID dos dois descritores locais com um snapshot novo da instância publicada. Preservar descrições/tags locais, URLs configuradas, handlers e todas as queries.
## Capabilities
Nenhuma mudança comportamental de spec. Reconciliação de identidade/configuração local, com skip_specs explícito; não há publicação remota nesta change.
## Impact
Dois arquivos api_group.xs, relatório e documentação. Sem alteração de .env, Swagger, secrets, schemas, registros, queries, código Reflex ou dependências. Nomes genéricos em URLs example.invalid dos testes permanecem fixtures fictícias.
