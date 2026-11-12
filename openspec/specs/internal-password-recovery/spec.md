# internal-password-recovery Specification

## Purpose

Permitir que um `UsuarioInterno` ativo recupere a própria senha por um token de uso único enviado por e-mail, sem revelar a existência de contas, sem autenticar automaticamente e sem expor credenciais.

## Requirements

### Requirement: Password recovery request is generic and does not enumerate accounts

The system SHALL allow an unauthenticated caller to request password recovery for an internal user by e-mail. The request SHALL always return the same generic success response, regardless of whether the e-mail exists, belongs to an inactive user or belongs to a user with an unapproved profile. The backend SHALL create a recovery token only for an active `UsuarioInterno` with role `FUNCIONARIO` or `ADMINISTRADOR`. The token SHALL expire after 60 minutes, SHALL be single-use and SHALL be stored only in hashed form. The request SHALL NOT return the token, a password, a hash or any credential, and SHALL NOT create an authentication session.

#### Scenario: Existing active user requests recovery

- **WHEN** an unauthenticated caller submits the e-mail of an active internal user
- **THEN** the backend creates a single-use token with a 60-minute expiration and sends the recovery message without returning the token or a session

#### Scenario: Unknown, inactive or unapproved e-mail

- **WHEN** an unauthenticated caller submits an e-mail that does not exist, belongs to an inactive user or belongs to a user outside the approved profiles
- **THEN** the backend returns the same generic success response and does not create a usable recovery token

#### Scenario: Repeated requests do not reveal account state

- **WHEN** the same e-mail is requested more than once
- **THEN** every response is indistinguishable in content and status from a request for a non-existent e-mail

#### Scenario: Request input is validated

- **WHEN** the submitted e-mail is missing, malformed or longer than 254 characters
- **THEN** the backend rejects the input with a client error and does not write a token

#### Scenario: Recovery is limited to internal users

- **WHEN** a `Cliente` e-mail or any record outside the `user` internal-user concept is submitted
- **THEN** it is not eligible for an internal recovery token and the generic response is preserved

### Requirement: Recovery token confirms a new password without authenticating the user

The system SHALL allow an unauthenticated caller to submit the e-mail, the recovery token, a new password and its confirmation. The backend SHALL accept the confirmation only when the token matches the stored hash, has not expired, has not been used, and the user is an active `UsuarioInterno` with an approved profile. The new password SHALL contain at least eight characters with at least one letter and one digit, SHALL match the confirmation and SHALL differ from the current password. A successful confirmation SHALL store the new password, mark the token as used and return a success result without a token, password, hash or session. Invalid, expired, reused or mismatched tokens SHALL be rejected with a generic client error that does not reveal whether the e-mail exists, and the stored password SHALL remain unchanged.

#### Scenario: Valid token sets a new password

- **WHEN** a valid unexpired unused token is submitted with a valid matching new password
- **THEN** the backend stores the new password, marks the token as used and returns success without creating a session or exposing credentials

#### Scenario: Invalid, expired or reused token is rejected

- **WHEN** the submitted token is wrong, expired or already used
- **THEN** the backend returns a generic client error, does not change the password and does not reveal account existence

#### Scenario: Invalid new password is rejected

- **WHEN** the new password is shorter than eight characters, lacks a letter or digit, equals the current password or does not match the confirmation
- **THEN** the backend rejects the confirmation without writing a password and without consuming the token

#### Scenario: Token is single-use

- **WHEN** the same valid token is submitted twice
- **THEN** the first confirmation changes the password and the second is rejected without changing it again

#### Scenario: Recovery cannot change another account

- **WHEN** a caller submits a target user identifier or another user's credentials through the recovery confirmation
- **THEN** only the account matching the e-mail and token can be affected and restricted input is rejected

#### Scenario: Inactive account cannot complete recovery

- **WHEN** the e-mail belongs to an inactive internal user or a user outside the approved profiles
- **THEN** the confirmation is rejected generically and no password is changed

### Requirement: Recovery credentials never appear in responses or logs

The system SHALL keep the recovery token, password, hash and session credentials out of every request and confirmation response. Error messages SHALL NOT include the token or distinguish between unknown e-mail, wrong token, expired token and used token. The backend SHALL NOT log the token value or the submitted passwords.

#### Scenario: Responses exclude credentials

- **WHEN** any recovery request or confirmation completes, successfully or not
- **THEN** the response contains only a generic result and no token, password, hash or authentication credential

#### Scenario: Errors are indistinguishable

- **WHEN** confirmation fails because the e-mail is unknown, the token is wrong, the token expired or the token was used
- **THEN** the caller receives the same generic error message and status for every case

### Requirement: Recovery interface is reachable and scoped to internal users

The internal login page SHALL offer a visible "Esqueci minha senha" entry. The recovery interface SHALL provide an e-mail request page and a new-password page. The new-password page SHALL read `email` and `token` from the URL and SHALL also allow manual entry when they are absent. The interface SHALL show a generic confirmation after a request, SHALL NOT display or persist the token, SHALL NOT report success before a confirmed response and SHALL keep the last confirmed state on failure. Styles SHALL remain scoped to the internal workspace.

#### Scenario: User requests recovery from the login page

- **WHEN** an unauthenticated internal user activates "Esqueci minha senha" and submits an e-mail
- **THEN** the interface shows the same generic confirmation for any e-mail and does not reveal whether the account exists

#### Scenario: User opens the reset link

- **WHEN** the reset page is opened with `email` and `token` in the URL
- **THEN** the page presents the new-password fields without displaying the token value in the visible content

#### Scenario: User resets with manual entry

- **WHEN** the reset page is opened without URL parameters
- **THEN** the page allows the user to enter the e-mail and the received token manually

#### Scenario: Reset feedback is truthful

- **WHEN** the confirmation succeeds or fails
- **THEN** success returns the user to the normal internal login, while failure keeps the submitted fields, shows an observable generic error and does not claim that the password changed
