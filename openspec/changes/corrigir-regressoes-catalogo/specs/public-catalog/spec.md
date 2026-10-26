## MODIFIED Requirements

### Requirement: Visitors can browse the public product catalog
O catálogo público SHALL permitir filtrar produtos ATIVO por categoria, quando fornecido o parâmetro `category_id` válido e correspondente a uma categoria ATIVA. Além do filtro por categoria, o catálogo público SHALL permitir filtrar por nome do produto quando fornecido o parâmetro opcional `q`. A busca por nome SHALL ser por correspondência parcial, case-insensitive, aplicada apenas ao campo `nome` dos produtos. O parâmetro `q` SHALL ser combinado com `category_id` quando ambos forem fornecidos (condição AND). Quando `q` for vazio ou composto apenas por espaços em branco, ele SHALL ser ignorado. A busca SHALL respeitar que apenas produtos ATIVO sejam considerados. O catálogo SHALL obter a URL assinada da imagem diretamente da resposta da listagem (campo `image_url`), sem emitir requisições HTTP individuais por produto. O formato da resposta, os endpoints públicos existentes e as demais regras do catálogo público SHALL permanecer inalterados.

#### Scenario: Anonymous visitor lists active products
- **WHEN** o visitante anônimo acessa a listagem pública sem parâmetros
- **THEN** são retornados apenas produtos ATIVO

#### Scenario: Product has an inactive category or brand association
- **WHEN** um produto ATIVO está associado a uma categoria INATIVA ou marca INATIVA
- **THEN** o catálogo público omite o nome da categoria/marca, sem excluir o produto

#### Scenario: Catalog read endpoint is called without authentication
- **WHEN** o endpoint público de leitura do catálogo é chamado sem autenticação
- **THEN** a resposta é obtida normalmente para produtos ATIVO

#### Scenario: Visitor filters products by name
- **WHEN** o visitante fornece o parâmetro `q` com parte do nome de um produto ATIVO
- **THEN** a listagem retorna apenas os produtos ATIVO cujo `nome` contenha o termo informado, sem distinção entre maiúsculas e minúsculas

#### Scenario: Visitor combines name search and category filter
- **WHEN** o visitante fornece `q` e `category_id` válido para uma categoria ATIVA
- **THEN** a listagem retorna apenas produtos ATIVO que atendam ao filtro por nome e pertençam à categoria selecionada

#### Scenario: Name search returns no results
- **WHEN** o parâmetro `q` não corresponde a nenhum produto ATIVO
- **THEN** a listagem retorna vazia e a interface apresenta o estado vazio

#### Scenario: Empty search term is ignored
- **WHEN** o parâmetro `q` é vazio ou contém apenas espaços em branco
- **THEN** o filtro por nome é ignorado e o comportamento é o mesmo da listagem sem busca

#### Scenario: Public catalog lists products with image URLs from response
- **WHEN** o catálogo público é carregado
- **THEN** as URLs de imagem são obtidas diretamente da listagem e o cache respeita a categoria e o termo de busca
