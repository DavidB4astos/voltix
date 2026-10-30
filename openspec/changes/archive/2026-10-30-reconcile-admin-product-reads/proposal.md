## Why
A auditoria encontrou drift nos GET products e variations administrativos. O publicado já exige user/ADMINISTRADOR/ATIVO, mas não coincide com a whitelist, ordenação e tipo explícito de erro previstos localmente.
## What Changes
Reconciliar apenas esses dois GETs com o contrato versionado: produtos por nome, variações por SKU, resposta explícita dos campos usados e leitura mínima de user id/role/status, mantendo guard antes dos dados. Vincular GUIDs às queries existentes e preparar publicação restrita revisável.
## Capabilities
### Modified Capabilities
- product-management: explicitar contrato das leituras administrativas no backend publicado.
## Impact
Dois GETs, testes de contrato e documentação. Sem alteração de dados, tabelas, APIs de escrita, URLs, credenciais, frontend/State, upload, catálogo público, estoque ou limites de paginação. Não adicionar novas permissões; os GETs publicados já são exclusivos do Administrador ativo.
