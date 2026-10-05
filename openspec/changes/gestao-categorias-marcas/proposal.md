## Why

A Voltix define Categoria e Marca como conceitos do catálogo, mas ainda não possui persistência nem operações para sua gestão. Esta Change estabelece uma administração mínima dessas duas entidades, com autorização restrita ao perfil `ADMINISTRADOR`, sem antecipar a implementação de produtos ou outras funções comerciais.

## What Changes

- Criar a gestão interna de Categoria e Marca, permitindo listar, criar, editar e alterar seu status entre `ATIVO` e `INATIVO`.
- Exigir nome obrigatório e único para cada entidade; permitir descrição opcional.
- Preservar registros inativos, sem exclusão definitiva.
- Aplicar a autorização de `ADMINISTRADOR` no backend para cada operação, além de controlar a apresentação das ações na interface.
- Usar a arquitetura `Interface Reflex -> State/lógica Python -> Xano`, mantendo as chamadas HTTP ao backend fora do código executado diretamente no navegador.

Ficam fora desta Change: produtos e variações, associação de produtos a categorias ou marcas, catálogo público, pesquisa, estoque, pedidos, permissões além desta gestão, dashboard, CRM e qualquer outro fluxo de negócio.

## Capabilities

### New Capabilities

- `catalog-management`: Gestão interna de categorias e marcas, autorizada somente a administradores.

### Modified Capabilities

Nenhuma.

## Impact

- Adiciona estruturas de dados e operações Xano/XanoScript para Categoria e Marca.
- Adiciona chamadas server-side no State Reflex e uma interface interna mínima para a gestão das duas entidades.
- Reutiliza a sessão de `UsuarioInterno` existente e acrescenta autorização backend específica para `ADMINISTRADOR`, sem alterar o acesso interno geral nem os fluxos de `Cliente`.
- Não requer novas dependências nem alterações às specs consolidadas existentes nesta etapa.
