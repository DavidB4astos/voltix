# reflex-xano-integration Specification

## Purpose

Estabelecer um contrato técnico mínimo e verificável para demonstrar que o frontend Reflex consegue consultar o backend Xano e interpretar sua resposta sem envolver funcionalidades de negócio.

## Requirements

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
- **THEN** ela ainda pode concluir somente o estado técnico da comunicação, sem criar, ler ou alterar registros do domínio.

### Requirement: Integration health behavior is covered by automated tests

The project SHALL maintain automated tests for the Xano health contract and for the frontend integration check without contacting the network or using domain records. The tests SHALL cover the exact success contract, missing configuration, HTTP failure, transport failure, invalid payload and retry.

#### Scenario: Successful health check is verified

- **WHEN** the automated suite exercises the health contract with a valid technical response
- **THEN** the test confirms that the integration is reported as available, the message identifies success and only the technical payload fields are preserved

#### Scenario: Missing configuration is verified

- **WHEN** the automated suite exercises the integration check without the required backend configuration
- **THEN** the test confirms that the failure is reported explicitly, no request is attempted to an implicit destination and the state does not report success

#### Scenario: Failures are verified without simulated success

- **WHEN** the automated suite exercises the integration check with an HTTP error, a transport failure or a response that does not match the expected contract
- **THEN** the test confirms that the state reports failure, preserves the distinction from success and does not retain a previous successful payload

#### Scenario: Retry after failure is verified

- **WHEN** an integration check fails and the automated suite triggers another check with a valid response
- **THEN** the test confirms that the state transitions from failure to success and the payload reflects only the new response

#### Scenario: Technical scope remains verified

- **WHEN** the automated suite inspects the health request and the backend health definition
- **THEN** it confirms that the request carries no authentication or domain data and that the response contract is exactly `status=ok`, `service=voltix-xano` and `integration=available`

### Requirement: Integration health tests remain isolated from external services

The automated tests for the integration health behavior SHALL use stubs or fakes for network calls and SHALL NOT depend on a running Reflex app or Xano instance.

#### Scenario: Suite runs without backend availability

- **WHEN** the integration health test suite runs in an environment where the backend is unreachable or unconfigured
- **THEN** every test still completes deterministically using controlled responses and no external call is attempted beyond the test stub
