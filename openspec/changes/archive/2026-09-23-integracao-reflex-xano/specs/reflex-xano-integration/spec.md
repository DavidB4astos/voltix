## Purpose

Estabelecer um contrato técnico mínimo e verificável para demonstrar que o frontend Reflex consegue consultar o backend Xano e interpretar sua resposta sem envolver funcionalidades de negócio.

## ADDED Requirements

### Requirement: Backend exposes an integration health contract

O backend SHALL disponibilizar um endpoint técnico, sem dependência de entidades de negócio, para verificar a disponibilidade da API Xano para o frontend.

#### Scenario: Backend is reachable

- **WHEN** um cliente HTTP consulta o endpoint técnico de integração com uma requisição válida
- **THEN** o backend responde com status HTTP de sucesso e um payload estruturado que identifica a integração como disponível

#### Scenario: Backend is unavailable

- **WHEN** o endpoint técnico não pode ser alcançado
- **THEN** a requisição falha de forma observável, sem produzir um resultado de sucesso simulado ou inventado

### Requirement: Reflex validates the Xano connection

O frontend SHALL permitir executar a verificação do endpoint técnico configurado e SHALL representar explicitamente os estados de carregamento, sucesso e falha da comunicação.

#### Scenario: Connection check succeeds

- **WHEN** o usuário inicia a verificação e o backend retorna o contrato de saúde esperado
- **THEN** o frontend informa que a integração Reflex-Xano foi validada e apresenta somente os dados técnicos retornados

#### Scenario: Connection check fails

- **WHEN** o usuário inicia a verificação e ocorre erro HTTP, resposta inválida ou falha de rede
- **THEN** o frontend informa que a integração não foi validada, preserva a distinção entre falha e sucesso e permite uma nova tentativa

### Requirement: Integration configuration is environment-specific

A URL ou base de acesso ao backend SHALL ser configurável por ambiente e o frontend SHALL evitar incluir credenciais, tokens ou endpoints privados diretamente no código-fonte versionado.

#### Scenario: Configured backend target is used

- **WHEN** a verificação é executada em um ambiente com a configuração obrigatória do backend disponível
- **THEN** a requisição utiliza esse destino configurado e não depende de um endereço fixo específico de desenvolvimento

#### Scenario: Backend target is missing

- **WHEN** a verificação é executada sem a configuração obrigatória do backend
- **THEN** o frontend apresenta uma falha de configuração explícita e não tenta uma chamada para um destino implícito

### Requirement: Business scope remains excluded

A validação desta integração MUST permanecer independente de autenticação, clientes, catálogo, carrinho, pedidos, pagamentos e CRM.

#### Scenario: Technical validation runs without domain data

- **WHEN** a verificação de integração é executada em uma instalação sem dados de negócio
- **THEN** ela ainda pode concluir somente o estado técnico da comunicação, sem criar, ler ou alterar registros do domínio
