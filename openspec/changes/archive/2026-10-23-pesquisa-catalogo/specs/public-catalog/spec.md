## MODIFIED Requirements

### Requirement: Visitors can browse the public product catalog

O cat�logo p�blico SHALL permitir filtrar produtos ATIVO por categoria, quando fornecido o par�metro `category_id` v�lido e correspondente a uma categoria ATIVA. Al�m do filtro por categoria, o cat�logo p�blico SHALL permitir filtrar por nome do produto quando fornecido o par�metro opcional `q`. A busca por nome SHALL ser por correspond�ncia parcial, case-insensitive, aplicada apenas ao campo `nome` dos produtos. O par�metro `q` SHALL ser combinado com `category_id` quando ambos forem fornecidos (condi��o AND). Quando `q` for vazio ou composto apenas por espa�os em branco, ele SHALL ser ignorado. A busca SHALL respeitar que apenas produtos ATIVO sejam considerados. O formato da resposta, os endpoints p�blicos existentes e as demais regras do cat�logo p�blico SHALL permanecer inalterados.

#### Scenario: Anonymous visitor lists active products
- **WHEN** o visitante an�nimo acessa a listagem p�blica sem par�metros
- **THEN** s�o retornados apenas produtos ATIVO

#### Scenario: Product has an inactive category or brand association
- **WHEN** um produto ATIVO est� associado a uma categoria INATIVA ou marca INATIVA
- **THEN** o cat�logo p�blico omite o nome da categoria/marca, sem excluir o produto

#### Scenario: Catalog read endpoint is called without authentication
- **WHEN** o endpoint p�blico de leitura do cat�logo � chamado sem autentica��o
- **THEN** a resposta � obtida normalmente para produtos ATIVO

#### Scenario: Visitor filters products by name
- **WHEN** o visitante fornece o par�metro `q` com parte do nome de um produto ATIVO
- **THEN** a listagem retorna apenas os produtos ATIVO cujo `nome` contenha o termo informado, sem distin��o entre mai�sculas e min�sculas

#### Scenario: Visitor combines name search and category filter
- **WHEN** o visitante fornece `q` e `category_id` v�lido para uma categoria ATIVA
- **THEN** a listagem retorna apenas produtos ATIVO que atendam ao filtro por nome e perten�am � categoria selecionada

#### Scenario: Name search returns no results
- **WHEN** o par�metro `q` n�o corresponde a nenhum produto ATIVO
- **THEN** a listagem retorna vazia e a interface apresenta o estado vazio

#### Scenario: Empty search term is ignored
- **WHEN** o par�metro `q` � vazio ou cont�m apenas espa�os em branco
- **THEN** o filtro por nome � ignorado e o comportamento � o mesmo da listagem sem busca
