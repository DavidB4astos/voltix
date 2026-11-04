# Revisão final — preços no painel de produtos

Data: 03/11/2026.

## Resultado

A tabela de variações do painel interno agora usa `_cart_money_text` nas células de preço e exibe o cabeçalho como “Preço”, sem repetir a unidade. O formatador apresenta valores como `R$ 119,90`. Valores de variações, formulários de edição/criação, cálculos, handlers e endpoints não foram modificados.

## Verificação

- `openspec validate format-internal-product-prices --strict`: aprovado.
- `git diff --check`: sem erros.
- Revisão estática confirmou que apenas o cabeçalho e a célula de exibição da tabela foram alterados no código funcional.
- Não foram executados testes automatizados nem QA visual no navegador.
- Lockfiles regenerados pela validação foram restaurados antes do encerramento.

## Limites

A mudança foi revisada por código e contrato OpenSpec; a tela não foi aberta em QA visual nesta etapa. Nenhum dado ou endpoint do Xano foi consultado ou alterado.
