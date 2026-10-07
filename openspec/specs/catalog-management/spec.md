# catalog-management Specification

## Purpose
Define the authorized internal management behavior for Voltix categories and brands, including their names, descriptions, statuses, and preservation as catalog records.

## Requirements

### Requirement: Administrators can manage categories

O sistema SHALL permitir que um `UsuarioInterno` autenticado, ativo e com perfil `ADMINISTRADOR` liste, crie e edite categorias. Cada categoria SHALL possuir nome obrigatório e único, descrição opcional e status `ATIVO` ou `INATIVO`; novos registros SHALL iniciar como `ATIVO`.

#### Scenario: Administrator lists categories
- **WHEN** um administrador autenticado solicita a lista de categorias
- **THEN** o sistema retorna as categorias ativas e inativas, incluindo seus nomes, descrições e status

#### Scenario: Administrator creates a category
- **WHEN** um administrador autenticado cria uma categoria com nome válido e ainda não utilizado
- **THEN** o sistema cria a categoria ativa com o nome e a descrição informados

#### Scenario: Category name is required
- **WHEN** um administrador tenta criar ou editar uma categoria sem nome
- **THEN** o sistema rejeita a operação e informa a validação sem criar ou alterar o registro

#### Scenario: Category name must be unique
- **WHEN** um administrador tenta criar ou renomear uma categoria para um nome já utilizado por outra categoria
- **THEN** o sistema rejeita a operação e preserva os registros existentes

#### Scenario: Administrator edits a category
- **WHEN** um administrador autenticado atualiza o nome válido ou a descrição de uma categoria existente
- **THEN** o sistema persiste os novos dados e mantém o status atual da categoria

### Requirement: Administrators can manage brands

O sistema SHALL permitir que um `UsuarioInterno` autenticado, ativo e com perfil `ADMINISTRADOR` liste, crie e edite marcas. Cada marca SHALL possuir nome obrigatório e único, descrição opcional e status `ATIVO` ou `INATIVO`; novos registros SHALL iniciar como `ATIVO`.

#### Scenario: Administrator lists brands
- **WHEN** um administrador autenticado solicita a lista de marcas
- **THEN** o sistema retorna as marcas ativas e inativas, incluindo seus nomes, descrições e status

#### Scenario: Administrator creates a brand
- **WHEN** um administrador autenticado cria uma marca com nome válido e ainda não utilizado
- **THEN** o sistema cria a marca ativa com o nome e a descrição informados

#### Scenario: Brand name is required
- **WHEN** um administrador tenta criar ou editar uma marca sem nome
- **THEN** o sistema rejeita a operação e informa a validação sem criar ou alterar o registro

#### Scenario: Brand name must be unique
- **WHEN** um administrador tenta criar ou renomear uma marca para um nome já utilizado por outra marca
- **THEN** o sistema rejeita a operação e preserva os registros existentes

#### Scenario: Administrator edits a brand
- **WHEN** um administrador autenticado atualiza o nome válido ou a descrição de uma marca existente
- **THEN** o sistema persiste os novos dados e mantém o status atual da marca

### Requirement: Categories and brands can be inactivated without deletion

O sistema SHALL permitir que administradores alterem o status de uma categoria ou marca entre `ATIVO` e `INATIVO`, preservando o registro e seus dados. A interface de gestão SHALL oferecer acesso aos registros de ambos os status para permitir sua reativação.

#### Scenario: Administrator inactivates a category or brand
- **WHEN** um administrador altera o status de uma categoria ou marca ativa para `INATIVO`
- **THEN** o sistema mantém o registro persistido e o apresenta como inativo na lista de gestão

#### Scenario: Administrator reactivates a category or brand
- **WHEN** um administrador altera o status de uma categoria ou marca inativa para `ATIVO`
- **THEN** o sistema mantém o mesmo registro persistido com status ativo

#### Scenario: Category or brand is not permanently deleted
- **WHEN** um administrador gerencia uma categoria ou marca existente
- **THEN** o sistema não oferece uma operação de exclusão definitiva

### Requirement: Catalog management is restricted to administrators

O sistema SHALL exigir, no backend e em cada operação de gestão de Categoria ou Marca, uma sessão válida de `UsuarioInterno` ativo com perfil `ADMINISTRADOR`. A interface SHALL apresentar os controles de gestão somente para administradores, sem tratar essa apresentação como substituta da autorização backend.

#### Scenario: Employee cannot manage categories or brands
- **WHEN** um `UsuarioInterno` com perfil `FUNCIONARIO` tenta listar ou alterar categorias ou marcas
- **THEN** o backend rejeita a operação e não retorna dados de gestão nem altera registros

#### Scenario: Unauthenticated request cannot manage categories or brands
- **WHEN** uma requisição de gestão é feita sem uma sessão válida
- **THEN** o backend rejeita a operação e não retorna dados nem altera registros

#### Scenario: Inactive administrator cannot manage categories or brands
- **WHEN** um usuário com perfil `ADMINISTRADOR` e status `INATIVO` tenta uma operação de gestão
- **THEN** o backend rejeita a operação e não retorna dados nem altera registros

### Requirement: Management errors remain observable

O sistema SHALL distinguir sucesso de falha nas operações de gestão, preservando os dados existentes quando uma operação é rejeitada ou falha.

#### Scenario: Backend rejects a management operation
- **WHEN** uma operação de gestão falha por validação, autorização ou indisponibilidade do backend
- **THEN** a interface informa que a operação falhou, não apresenta sucesso simulado e permite nova tentativa quando aplicável
