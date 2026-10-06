## Why

A Voltix precisa apresentar seus produtos ao público antes da implementação dos fluxos de compra. A mudança disponibiliza navegação e detalhes do catálogo sem login, mantendo os dados e operações administrativas existentes separados.

## What Changes

- Adicionar uma capacidade de catálogo público com listagem de produtos `ATIVO`, detalhes do produto e suas variações `ATIVO`.
- Apresentar informações comerciais disponíveis no domínio, incluindo preço e quantidade disponível da variação; estoque zero continua distinto de variação inativa e será indicado como indisponível para compra, sem implementar compra.
- Permitir navegação/filtro pelas categorias `ATIVO`; não alterar nem remover associações existentes entre produto, categoria e marca.
- Disponibilizar imagem principal quando cadastrada, sem tornar público o caminho privado original do arquivo.
- Permitir acesso anônimo à página pública e às operações de leitura necessárias, sem alterar os endpoints de gestão.
- Excluir carrinho, checkout, pedidos, pagamentos, cadastro de cliente, CRM e novas funcionalidades administrativas.

## Capabilities

### New Capabilities

- `public-catalog`: Consulta anônima de produtos e variações ativos, detalhes e navegação por categorias ativas.

### Modified Capabilities

Nenhuma.

## Impact

- Adiciona uma página pública Reflex e lógica State/Python para consultar Xano sem autenticação, mantendo as chamadas HTTP fora do código executado diretamente no navegador.
- Adiciona operações Xano somente de leitura e acesso anônimo, com projeção restrita aos dados necessários para o catálogo.
- Reutiliza Produto, VariacaoProduto, Categoria e Marca existentes. Produtos e associações não são alterados; endpoints administrativos permanecem intactos.
- A imagem armazenada como arquivo privado deverá ser disponibilizada ao catálogo por URL temporária assinada, quando houver imagem; o caminho privado não será exposto como URL pública.
- Não introduz dependências, serviços ou estruturas de dados de domínio.
