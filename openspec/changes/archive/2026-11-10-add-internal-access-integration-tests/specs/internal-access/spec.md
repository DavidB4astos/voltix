## ADDED Requirements

### Requirement: Internal access behavior is covered by automated tests

The project SHALL maintain automated tests that exercise the internal authentication and authorization contract without contacting Xano, using isolated fixtures and no real customer or internal-user records. The tests SHALL cover successful login, rejected credentials, identity validation, protected-area authorization, logout and separation between Cliente and UsuarioInterno.

#### Scenario: Successful login is verified

- **WHEN** the automated suite exercises login with valid credentials and a well-formed backend response
- **THEN** the test confirms that a non-empty token and the returned internal user identifier are stored, the local session is marked authenticated and no password or token is exposed in the presentation payload

#### Scenario: Invalid credentials and malformed responses are verified

- **WHEN** the automated suite exercises login with rejected credentials, a malformed response, a missing token, a non-numeric identifier or a transport failure
- **THEN** the test confirms that no authenticated session is created and the local authentication fields remain empty

#### Scenario: Identity validation is verified

- **WHEN** the automated suite exercises session validation with an approved active profile, an unapproved profile, an inactive status, a missing token or a rejected protected-area check
- **THEN** the test confirms that only the approved active identity keeps the session authenticated and that every other case clears the local session

#### Scenario: Logout is verified

- **WHEN** an authenticated internal user triggers logout in the automated suite
- **THEN** the test confirms that the token, identity, internal data and protected-area access are removed and the workspace returns to the unauthenticated state

#### Scenario: Customer separation is verified

- **WHEN** the automated suite presents client credentials or a client profile to the internal access flow
- **THEN** the test confirms that the record is not accepted as FUNCIONARIO or ADMINISTRADOR and does not receive internal access

#### Scenario: Backend guards remain enforced

- **WHEN** the automated suite inspects the internal authentication and access definitions
- **THEN** it confirms that login, identity and protected access accept only the approved profiles and `ATIVO` status, return `accessdenied` otherwise, and do not expose password or token in identity responses

### Requirement: Internal access tests remain isolated from external services

The automated tests for internal access SHALL use stubs or fakes for backend calls and SHALL NOT perform network requests, create sessions in Xano or read real records.

#### Scenario: Suite runs without Xano availability

- **WHEN** the internal-access test suite runs in an environment where Xano is unreachable or unconfigured
- **THEN** every test still completes deterministically using controlled responses and no external call is attempted beyond the test stub
