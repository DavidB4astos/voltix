# Padronizar a exibição de preços no painel de produtos

## Why

A tabela de variações apresenta o preço convertido diretamente em texto (`119.9`), sem vírgula decimal nem duas casas. Isso dificulta a leitura de um valor comercial.

## What Changes

- Exibir o preço de cada variação como moeda brasileira, com prefixo `R$`, vírgula decimal e duas casas.
- Remover a indicação redundante `(R$)` do cabeçalho da coluna, pois cada valor exibirá a moeda.
- Preservar o valor recebido, armazenado e enviado nos formulários; somente a apresentação da tabela muda.

## Fora do escopo

- Alterar preços, regras de validação, endpoints, payloads ou dados no Xano.
- Modificar formulários, catálogo público, carrinho, checkout ou pedidos.
- Alterar arredondamento ou cálculos financeiros.

## Impacto

Somente a tabela de variações no painel interno e a especificação `product-management`.
