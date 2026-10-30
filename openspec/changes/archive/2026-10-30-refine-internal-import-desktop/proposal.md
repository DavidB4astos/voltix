## Why
A importação usa instruções extensas e um card por linha, dificultando distinguir seleção, revisão e resultado em arquivos com várias linhas. O painel interno já possui um padrão desktop mais legível.
## What Changes
Separar orientações e área de trabalho; destacar formatos/limites existentes, seleção de arquivo, prévia tabular e relatório final tabular. Mostrar progresso/feedback e confirmação explícita com ações existentes.
## Capabilities
### Modified Capabilities
- product-bulk-import: apresentação desktop acessível e clara das etapas já existentes.
## Impact
Somente apresentação Reflex e CSS escopado. Preservar State, handlers, parsing CSV/XLSX, limites 200 linhas/50 produtos/2 MB, validações, autorização, cancelamento e regras de duplicidade. Sem novos endpoints, dependências, download de modelo ou importação real para QA.
