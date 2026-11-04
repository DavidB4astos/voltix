## Why
A auditoria somente leitura do Xano registrou que o campo `image_file` do endpoint de imagem aparece opcional na representação publicada e obrigatório na definição local. O upload também tem uma limitação histórica de HTTP 403 no plano usado, sem prova recente de funcionamento. Precisamos determinar, pelo OpenSpec, se o formulário Reflex, o endpoint Xano local e a definição publicada têm um contrato compatível e quais limitações impedem uma conclusão operacional.

## What Changes
- Comparar o multipart enviado pelo painel com o input do endpoint Xano local e publicado.
- Revisar guarda de administrador ativo, formato da resposta, armazenamento e atualização do produto.
- Verificar o registro histórico de HTTP 403 e distinguir evidência antiga de estado atual.
- Documentar achados e recomendar se o fluxo pode ser considerado operacional ou se exige uma change funcional separada.

## Capabilities
Nenhuma capability funcional alterada. `skip_specs: true` porque a entrega proposta é uma análise documental, sem mudar comportamento.

## Impact
Somente leitura e documentação. Não enviar imagem, não executar POST no endpoint, não publicar ou alterar schema Xano, não mudar arquivo de código, produto, imagem, registro ou plano/serviço. Qualquer proposta de correção funcional será tratada como uma change separada, com aprovação própria.
