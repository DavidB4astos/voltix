# Design — preços no painel interno

## Decisão

Usar o formatador de moeda já existente `_cart_money_text` para exibir as células da tabela, mantendo a mesma apresentação monetária usada em carrinho e pedidos. Remover `(R$)` do rótulo da coluna, pois a unidade passa a acompanhar cada valor.

## Restrições

- Não alterar `variation.price` nem o valor usado em edição/criação.
- Não alterar o helper de moeda ou qualquer outra tela.
- Preservar ordenação, handlers, dados e permissões.

## Verificação

Inspecionar o diff para confirmar o uso do formatador somente na tabela interna e a preservação dos fluxos de edição. Validar com OpenSpec estrito e `git diff --check`. Sem mutações remotas.
