## Why
O detalhe atual empilha uma foto larga e informações sem hierarquia, deixando preço e compra abaixo da primeira área visível. Há títulos H1 repetidos e o preço 499.9 não tem apresentação monetária adequada.

## What Changes
- Painel editorial em duas colunas no desktop, com imagem inteira e crédito aprovado, placeholder honesto quando não houver foto.
- Nome em H2, marca/categoria secundárias, descrição e especificações legíveis, variações com nome/SKU, preço em reais com duas casas e estoque real.
- Botão de compra com nome acessível por variação, estado desabilitado preservado e explicação de uma unidade por acionamento.
- Fechar detalhes visível, feedback existente e links de conta/carrinho preservados.

## Capabilities
### Modified Capabilities
- public-catalog: apresentação acessível dos detalhes sem alterar regras comerciais.

## Impact
Apenas composição do painel e CSS escopado; sem alteração de handlers, State, APIs, dados, autenticação, quantidade adicionada, navegação, filtros ou catálogo. Sem novo seletor de quantidade, galeria, preço promocional ou dados inventados. Layout abaixo de 1024px empilhado apenas para evitar regressão; foco de avaliação é desktop. Carregamento e erro/retry existentes permanecem visíveis.
