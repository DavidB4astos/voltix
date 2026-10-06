## Why

A Voltix ainda não possui uma forma administrativa de manter produtos, embora o Domain Model defina Produto como parte central do catálogo. Esta Change permitirá que ADMINISTRADOR cadastre e mantenha produtos válidos, relacionados às Categorias e Marcas existentes e com ao menos uma variação comercial.

## What Changes

- Adicionar gestão interna de Produto para ADMINISTRADOR: listar, criar, editar e inativar/reativar registros; preservar registros associados a histórico comercial.
- Associar cada Produto a exatamente uma Categoria e uma Marca existentes.
- Incluir a gestão mínima de `VariacaoProduto` necessária para que todo Produto tenha ao menos uma variação, com SKU obrigatório e globalmente único, preço maior que zero, quantidade disponível não negativa e status `ATIVO`/`INATIVO`; novos Produtos e variações começam `ATIVO`.
- Manter no Produto os atributos definidos no Domain Model — nome, descrição, especificações técnicas, imagem principal, status e auditoria — e permitir somente uma imagem principal opcional, armazenada no Xano. A Change não define obrigatoriedade adicional para nome, descrição ou especificações.
- Usar `Interface Reflex -> State/lógica Python -> Xano`, com autorização de `ADMINISTRADOR` validada no backend.

Ficam fora desta Change: catálogo público, pesquisa, carrinho, pedidos, pagamentos, CRM, estoque como entidade ou movimentações, galeria de imagens, exclusão definitiva e quaisquer outros fluxos de negócio. A Change não altera as regras de domínio documentadas.

## Capabilities

### New Capabilities

- `product-management`: Gestão administrativa de Produtos e de suas variações comerciais mínimas.

### Modified Capabilities

Nenhuma.

## Impact

- Adiciona persistência e operações Xano/XanoScript para Produto e `VariacaoProduto`, relacionadas às estruturas existentes de Categoria e Marca.
- Adiciona chamadas server-side no State Reflex e interface interna administrativa, incluindo seleção de Categoria/Marca e imagem principal opcional armazenada no Xano.
- Reutiliza sessão e padrões de autorização de usuário interno existentes; não exige novas dependências ou alteração dos fluxos de Cliente.
