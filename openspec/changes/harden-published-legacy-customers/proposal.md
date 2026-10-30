## Why
A auditoria encontrou quatro aliases legados de clientes publicados sem auth/ownership/whitelist, apesar de as proteções já estarem versionadas localmente. A atualização do próprio perfil usa PATCH /cliente/{cliente_id}; desativar todo o grupo quebraria Minha conta.
## What Changes
Publicar somente os quatro aliases protegidos já existentes no repositório: GET /cliente retorna apenas a identidade autenticada; GET/PATCH /cliente/{cliente_id} exigem propriedade e Cliente ativo; PATCH aceita somente nome/e-mail/telefone; DELETE fica bloqueado sem db.del. Preservar GUIDs, grupo e canonical em uso.
## Capabilities
### Modified Capabilities
- customer-access: exigir as proteções dos aliases no backend publicado e validar o pacote restrito.
## Impact
Quatro queries Xano; sem nova feature, sem alteração de frontend/State, schemas, registros, signup POST, login, credenciais, env, outros grupos, estoque ou canonical. Publicação somente após revisão concreta do dry-run. Testes remotos inicialmente negativos, sem corpos privados nem mudanças em clientes reais.
