## Why
A sincronização Xano de 30/10/2026 apontou diferenças entre defaults locais e a representação publicada para os campos `endereco.principal` e `pedido.valor_frete`. Uma conferência somente de metadados e dos caminhos de escrita do aplicativo deve registrar se a divergência afeta os fluxos atuais, sem inserir dados ou alterar o Xano.

## What Changes
- Registrar os campos e diferenças confirmados entre XanoScript local e a cópia de metadados publicada no workspace.
- Verificar estaticamente se os endpoints atuais enviam valores explícitos ao persistir endereço e pedido.
- Atualizar o registro da auditoria e o roadmap com o resultado e seus limites.

## Capabilities
Nenhuma capability funcional alterada. `skip_specs: true`; esta change é somente documental e de auditoria.

## Impact
Somente documentação e evidências sanitizadas. Sem alteração de código, schema, registros, configuração, publicação ou teste que escreva dados no Xano. Não afirmar qual valor o banco aplica quando uma inserção omite o campo: esse comportamento não foi exercitado.
