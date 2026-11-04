# Revisão final — defaults do schema Xano

Data: 03/11/2026.

- Escopo concluído: conferência somente de metadados publicados e revisão estática dos caminhos locais de persistência.
- `endereco.principal` e `pedido.valor_frete` não têm defaults explícitos na cópia publicada; os endpoints atuais enviam valores explicitamente.
- O comportamento do runtime para inserções sem esses valores continua desconhecido. Nenhum registro, schema, query, configuração ou arquivo de aplicação foi alterado no Xano.
- A diferença e seus limites foram acrescentados à auditoria Xano e ao roadmap.
- Change documental sem alteração de specs (`skip_specs: true`), validada em modo estrito, revisada e arquivada. Nenhuma suíte funcional foi executada, pois não houve alteração executável.
