# customer-addresses Specification

## Purpose
Specify the private address book of an authenticated Voltix Customer, enforcing ownership and the Domain Model's primary-address, status, and order-history preservation rules.

## Requirements

### Requirement: Customers can manage their own addresses
O sistema SHALL permitir que um Cliente `ATIVO` autenticado liste, cadastre e edite seus próprios Endereços, com CEP, logradouro, número, complemento, bairro, cidade, estado, identificação, indicador de endereço principal e status definidos no Domain Model. Novos Endereços SHALL iniciar `ATIVO`. Nenhum campo além dos previstos no Domain Model SHALL ser exigido como regra de negócio nova.

#### Scenario: Customer lists own addresses
- **WHEN** um Cliente autenticado consulta seus endereços
- **THEN** o sistema retorna somente Endereços pertencentes àquele Cliente, incluindo ativos e inativos

#### Scenario: Customer creates an address
- **WHEN** um Cliente autenticado cadastra um endereço válido
- **THEN** o backend associa o registro ao Cliente da sessão e o cria como `ATIVO`

#### Scenario: Customer edits own address
- **WHEN** um Cliente autenticado edita um de seus Endereços
- **THEN** somente os campos de endereço permitidos do registro próprio são atualizados

#### Scenario: Customer cannot access another customer's address
- **WHEN** o Cliente tenta consultar, editar, inativar ou remover endereço pertencente a outro Cliente
- **THEN** o backend rejeita a operação e não divulga nem altera o endereço de terceiro

#### Scenario: Unauthenticated caller cannot manage addresses
- **WHEN** uma requisição de gestão de Endereço não possui sessão válida de Cliente `ATIVO`
- **THEN** o backend rejeita a operação sem retornar ou alterar endereços

### Requirement: A customer has at most one active primary address
O backend SHALL preservar no máximo um endereço principal por Cliente. Marcar um endereço como principal SHALL remover o indicador de principal dos demais endereços daquele Cliente de forma consistente. Ao inativar um endereço principal, o backend SHALL remover automaticamente seu indicador; o Cliente não SHALL ser obrigado a designar outro principal imediatamente.

#### Scenario: Customer sets a primary address
- **WHEN** o Cliente marca um de seus endereços como principal
- **THEN** somente esse endereço permanece principal entre os endereços daquele Cliente

#### Scenario: Customer inactivates the primary address
- **WHEN** o Cliente inativa seu endereço principal
- **THEN** o endereço permanece registrado como `INATIVO` e deixa de ser principal, sem exigir outro endereço principal

#### Scenario: Inactive address is reactivated
- **WHEN** o Cliente reativa um endereço próprio inativo
- **THEN** o mesmo registro volta a `ATIVO` e não se torna principal automaticamente

### Requirement: Address removal preserves order history
O sistema SHALL permitir remoção definitiva somente de Endereço próprio que não seja referenciado por Pedido. Um Endereço referenciado por Pedido SHALL ser preservado e poderá ser inativado; um Endereço `INATIVO` não SHALL ser elegível para novos Pedidos. Esta Change não implementa Pedidos nem seleção de endereço em compra.

#### Scenario: Unused address is removed
- **WHEN** o Cliente solicita a remoção de um endereço próprio sem referência a Pedido
- **THEN** o backend remove o endereço definitivamente

#### Scenario: Address referenced by an order is preserved
- **WHEN** o Cliente tenta remover um endereço referenciado por Pedido
- **THEN** o backend rejeita a remoção e preserva o endereço e a referência histórica

#### Scenario: Inactive address cannot be used for a future order
- **WHEN** um fluxo posterior tenta usar endereço `INATIVO` para novo Pedido
- **THEN** o sistema rejeita sua seleção

### Requirement: Address operations use the Reflex State and server-side Xano flow
A interface SHALL encaminhar listagem, criação, edição, mudança de status e remoção de Endereço ao State/lógica Python; essa camada SHALL executar as chamadas HTTP ao Xano. O backend SHALL aplicar autorização e propriedade independentemente da interface.

#### Scenario: Address request uses server-side State
- **WHEN** o Cliente executa uma operação de endereço pela interface
- **THEN** o State/Python efetua a chamada HTTP ao Xano e não há comunicação de dados direta do navegador ao backend

#### Scenario: Address operation fails
- **WHEN** o backend rejeita uma operação ou ocorre falha de rede
- **THEN** a interface informa a falha e não apresenta a alteração como persistida
