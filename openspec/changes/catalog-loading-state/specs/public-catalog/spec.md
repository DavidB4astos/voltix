## ADDED Requirements

### Requirement: Public catalog distinguishes initial loading, empty, and populated states

O catálogo público SHALL apresentar estados visuais distintos e mutuamente exclusivos para a primeira carga da sessão: carregamento enquanto a consulta inicial ao backend não tiver sido concluída, lista vazia somente quando a carga inicial estiver concluída sem produtos disponíveis, e grade de produtos quando houver produtos. Antes da conclusão da primeira carga, o sistema SHALL NOT apresentar o estado de lista vazia como se o catálogo não tivesse produtos.

#### Scenario: Initial load in progress shows loading state
- **WHEN** um visitante abre o catálogo público antes de a primeira carga de dados da sessão ser concluída
- **THEN** a interface apresenta o estado de carregamento e não apresenta o estado de lista vazia nem a grade de produtos

#### Scenario: Completed load with no products shows empty state
- **WHEN** a primeira carga é concluída e não há produtos públicos disponíveis
- **THEN** a interface apresenta o estado de lista vazia

#### Scenario: Completed load with products shows the product list
- **WHEN** a primeira carga é concluída e há produtos públicos disponíveis
- **THEN** a interface apresenta a grade de produtos e não apresenta os estados de carregamento nem de lista vazia

#### Scenario: Failed initial load remains observable
- **WHEN** a primeira carga termina em falha após o tratamento de erros
- **THEN** a interface apresenta o estado de falha com nova tentativa e não apresenta o estado de lista vazia como resultado
