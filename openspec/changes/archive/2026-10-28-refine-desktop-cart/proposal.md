## Why
O carrinho atual empilha campos e ações sem hierarquia, usa entrada de quantidade sem rótulo explícito e separa o total do fluxo visual de revisão. Precisamos melhorar leitura e controles no desktop sem alterar cálculos ou regras do Xano.

## What Changes
- Itens editoriais com nome, variação/SKU, disponibilidade, preço unitário, quantidade confirmada e subtotal.
- Formulário rotulado para editar quantidade, atualização explícita e remoção com nomes acessíveis específicos.
- Duas colunas desktop: itens e resumo dos valores confirmados; retorno ao catálogo e continuação para checkout sem botão aninhado em link.
- Desabilitar ações durante carregamento, preservar feedback e dados confirmados, sem confundir carregamento ou falha inicial com carrinho vazio confirmado.
- Formatar valores decimais por texto, sem converter para float nem recalcular total. Exibir ao menos duas casas, preservando precisão extra recebida.
- Separar composição pura do carrinho para prévia isolada autorizada pelo usuário, com dados fictícios e sem chamada Xano.

## Capabilities
### Modified Capabilities
- shopping-cart: apresentação desktop e acessibilidade dos controles existentes.

## Impact
Sem mudança de autenticação, eventos de mutação, payloads, cálculo, limite de estoque, quantidade zero/remove ou checkout. Sem fotos inventadas, frete, descontos ou promessa de reserva. Não redesenhar mobile; manter empilhamento seguro. A prévia de teste fica fora do aplicativo e não cria rota de bypass de autenticação.
