## Why

Atualmente o catálogo público permite filtrar apenas por categoria (`category_id`). Para melhorar a descoberta de produtos no storefront, é necessário permitir que o visitante pesquise por **nome do produto** diretamente a partir da listagem, sem sair da página e sem alterar o fluxo de navegação por categoria.

## What Changes

- Adicionar suporte a busca por nome do produto no endpoint público de listagem `GET /products` (XanoScript), aceitando um parâmetro opcional `q` (consulta textual).
- Manter compatibilidade com o filtro existente por `category_id` e com suas regras (apenas categorias ativas).
- Implementar busca case-insensitive por correspondência parcial (substring) no campo `nome` do produto, sem alterar estrutura de tabelas/entidades.
- Atualizar o cliente Reflex (`voltix/voltix.py`) para enviar `q` quando houver termo de busca, integrar com os estados existentes de carregamento/vazio/erro e manter o comportamento de cache/limites já definidos para o catálogo público.
- Atualizar testes em `tests/test_public_catalog.py` para cobrir o novo parâmetro e os novos cenários (busca + categoria, busca sem resultados, etc.).

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `public-catalog`: adicionar requisito de pesquisa textual por **nome do produto** (parâmetro `q`) com busca parcial case-insensitive, combinável com filtro por categoria ativa, sem alterar contratos existentes exceto o novo parâmetro opcional; preservar limites de requisições, tratamento de 429, estados (loading/empty/loaded), logs sem dados sensíveis e demais regras vigentes.

## Impact

- **Backend**: `xano/api/public_catalog/products_GET.xs` - adicionar input `q` (text?), aplicar filtro em `where` usando operador adequado ao XanoScript para busca parcial case-insensitive em `nome`, manter lógica por categoria e resposta no mesmo formato.
- **Frontend**: `voltix/voltix.py` - adicionar UI de busca (input) no catálogo público, conectar ao `State`, atualizar `_fetch_public_products` para passar `q`, manter cache/controle de requisições concorrentes/rate limiting existentes.
- **Testes**: `tests/test_public_catalog.py` - ampliar cobertura.
- **Specs**: delta em `openspec/specs/public-catalog/spec.md`.
- **Docs**: atualizar `docs/roadmap-changes.md` após criação dos artefatos.
- **Limites**: não alterar banco, outros endpoints, dependências/lockfiles, não executar servidor/builds/testes demorados ou chamadas Xano desnecessárias. SKU/descrição não entram no escopo neste momento (apenas nome).
