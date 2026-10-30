## MODIFIED Requirements

### Requirement: Administrators can list products
The system SHALL allow an authenticated, active `UsuarioInterno` with profile `ADMINISTRADOR` to list products and their variations, including product data, category and brand references, image presence, and current statuses. Published GET products and GET variations SHALL enforce user-table authentication and active ADMINISTRADOR authorization before querying business records. User lookup SHALL expose only id, role and status. Products SHALL be ordered by nome ascending and return only id, nome, descricao, especificacoes_tecnicas, imagem_principal, categoria_id, marca_id, status, created_at and updated_at. Variations SHALL be ordered by sku ascending and return only id, produto_id, nome_ou_descricao, sku, preco, quantidade_disponivel, status, created_at and updated_at. These reads SHALL preserve inactive records for administrative maintenance, remain non-mutating and report access denial explicitly.

#### Scenario: Administrator lists products
- **WHEN** an authorized administrator requests the product list
- **THEN** the system returns persisted products with their category, brand, variations, and statuses

#### Scenario: Non-administrator cannot list products
- **WHEN** a `FUNCIONARIO`, inactive user, or unauthenticated caller requests the product list
- **THEN** the backend rejects the request without returning product data

#### Scenario: Administrative read fields remain bounded
- **WHEN** an authorized administrator requests products or variations
- **THEN** the response remains a list of the approved fields, in the specified ascending order, without exposing unrelated user fields or silently hiding inactive catalog records

#### Scenario: Read denial precedes catalog access
- **WHEN** authentication is missing or invalid, or the user is not an active administrator
- **THEN** access is denied before reading product or variation business data and no record is modified
