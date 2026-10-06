## Why

Clientes autenticados já podem consultar o catálogo e manter sua conta, mas ainda não têm um local persistente para organizar variações que pretendem comprar. Esta Change implementa o Carrinho previsto no Domain Model, sem iniciar o fluxo de compra.

## What Changes

- Criar e preservar no máximo um Carrinho ativo por Cliente autenticado, permitindo que permaneça vazio.
- Permitir adicionar variações de produtos, consultar itens, alterar quantidades e remover itens.
- Validar no backend status ativo de Produto/Variação e estoque disponível para adição e alteração de quantidade.
- Exibir quantidade, preço atual da variação, subtotal por item e total do carrinho.
- Manter o fluxo de dados Reflex → State/lógica Python → Xano e impedir acesso ao carrinho de outro Cliente.

Ficam fora do escopo checkout, criação de Pedido, pagamento, frete, CRM e reserva ou baixa de estoque.

## Capabilities

### New Capabilities

- `shopping-cart`: Carrinho persistente do Cliente e operações owner-scoped para administrar itens e totais.

### Modified Capabilities

Nenhuma capacidade existente precisa mudar seus requisitos; catálogo, gestão de produtos e acesso de Cliente permanecem como contratos já definidos.

## Impact

- Adiciona persistência e endpoints Xano/XanoScript para Carrinho e ItemCarrinho, associados ao Cliente autenticado e às variações existentes.
- Acrescenta chamadas server-side no State/Python, configuração de ambiente e interface do Cliente.
- Reutiliza a sessão separada de Cliente e as estruturas Produto/VariacaoProduto existentes; não altera autenticação interna, administração ou endpoints públicos do catálogo.
