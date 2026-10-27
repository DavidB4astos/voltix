## Why
O endpoint público já aceita q para busca parcial por nome e combinação AND com category_id. O estado e cache também aceitam o termo, mas o catálogo não oferece campo de busca. O usuário autorizou a próxima etapa após o rodapé.

## What Changes
- Formulário de busca pelo nome com rótulo, botão Buscar e Enter; digitar não dispara requisições.
- Combinar busca aplicada e categoria; Limpar filtros remove ambos e detalhes selecionados.
- Mostrar termo aplicado, contagem e mensagem específica sem resultados, preservando erro/retry e carregamento.
- URL /catalogo?q=...&category_id=... representa os filtros aplicados e permite reabrir/compartilhar a consulta. A entrada contextual product_id permanece válida.
- Separar rascunho do campo do termo aplicado; limitar a 100 caracteres na interface e na entrada de URL/formulário, aparando espaços nas extremidades.
- Não mudar o header/Home nesta etapa. Apenas o catálogo recebe os controles; manter responsividade básica sem redesenho mobile.

## Capabilities
### Modified Capabilities
- public-catalog: interface de busca usando contrato público existente.

## Out of Scope
Mudança de API/Xano, busca específica por marca, autocomplete, indexação, novos endpoints, dados, preços, autenticação, regras de compra ou dependências. Não publicar nem incluir mudanças anteriores de outras áreas.
