## ADDED Requirements

### Requirement: Administrators can list and create internal users

The system SHALL allow an authenticated `UsuarioInterno` with role `ADMINISTRADOR` and
status `ATIVO` to list all internal users and create a new one. The backend SHALL authorize
the session before reading or writing user records. The list SHALL return every internal
user, including inactive ones, ordered by name ascending, exposing only `id`, `name`,
`email`, `role`, `status` and `created_at`. Creation SHALL require a name, a valid and unique
email, a password with at least eight characters containing at least one letter and one
digit, and a role of `FUNCIONARIO` or `ADMINISTRADOR`; the new user SHALL start with status
`ATIVO`. A duplicate email SHALL be rejected with a client error, including against an
inactive user, and SHALL NOT create a record. Creation SHALL NOT return a password, hash,
token, `password_reset` or `account_id`, and SHALL NOT authenticate the new user
automatically.

#### Scenario: Administrator lists internal users

- **WHEN** an active administrator requests the internal user list
- **THEN** the backend returns all internal users ordered by name with only the approved fields, including inactive users

#### Scenario: Administrator creates an internal user

- **WHEN** an active administrator submits a valid name, unique email, valid initial password and approved role
- **THEN** the backend creates the user with status `ATIVO` and returns the approved fields without credentials

#### Scenario: Duplicate email is rejected

- **WHEN** an active administrator tries to create a user with an email already used by another internal user, active or inactive
- **THEN** the backend rejects the creation with a client error and does not create a user

#### Scenario: Invalid creation data is rejected

- **WHEN** an active administrator submits a missing name, invalid email, weak password or role outside the approved values
- **THEN** the backend rejects the creation without writing a user

#### Scenario: Non-administrators cannot list or create users

- **WHEN** a `FUNCIONARIO`, an inactive internal user, a `Cliente` session, a visitor or an unauthenticated caller requests the user list or creates a user
- **THEN** the backend denies access before reading or writing user records

### Requirement: Administrators can edit internal users without deleting them

The system SHALL allow an active `ADMINISTRADOR` to partially update an existing internal
user's name, email, role and status. The backend SHALL respond with a not-found error when
the target user does not exist and SHALL reject a duplicate email excluding the target user.
The update SHALL NOT accept or change a password, SHALL NOT delete the user, and SHALL
preserve historical attendance references through inactivation. The authenticated
administrator SHALL NOT change their own role or status. An update that would remove the
last active administrator SHALL be rejected without writing. Successful responses SHALL use
the same bounded field allowlist as the list operation.

#### Scenario: Administrator edits another user

- **WHEN** an active administrator updates the name, email, role or status of another internal user with valid values
- **THEN** the backend persists the approved fields and returns the updated user without credentials

#### Scenario: Inactivation preserves history

- **WHEN** an active administrator sets another user's status to `INATIVO`
- **THEN** the user record and its historical references are preserved, and new authentication is denied by the existing login guard

#### Scenario: Administrator protects their own access

- **WHEN** an active administrator tries to change their own role or status
- **THEN** the backend rejects the update without writing and keeps the current role and status

#### Scenario: Last active administrator is protected

- **WHEN** an update would leave no active administrator
- **THEN** the backend rejects the update without writing

#### Scenario: Unknown user or duplicate email is rejected

- **WHEN** an active administrator targets a missing user or an email already used by another internal user
- **THEN** the backend responds with a not-found or client error respectively and does not write

#### Scenario: Passwords and deletion are unavailable to administration

- **WHEN** an active administrator attempts to update a password or delete an internal user through the management endpoints
- **THEN** the operation is not accepted and no password or record is changed

### Requirement: Internal users can maintain their own profile

The system SHALL allow an active `UsuarioInterno` with role `FUNCIONARIO` or
`ADMINISTRADOR` to read and partially update their own name and email. The backend SHALL
authorize the session and status before writing. The profile update SHALL NOT accept role,
status, password, `account_id` or any other field, SHALL reject a duplicate email excluding
the current user, and SHALL NOT modify another user's record. The response SHALL expose only
`id`, `name`, `email`, `role` and `status` and SHALL NOT expose password, hash, token or
`password_reset`.

#### Scenario: User updates their own name or email

- **WHEN** an active internal user submits a valid new name or unique email
- **THEN** the backend persists only the approved profile fields and returns the confirmed identity without credentials

#### Scenario: Profile cannot escalate privileges

- **WHEN** a user submits role, status, password or another restricted field through the profile update
- **THEN** the backend does not apply the restricted field and the user's permissions remain unchanged

#### Scenario: Duplicate profile email is rejected

- **WHEN** an active internal user submits an email already used by another internal user
- **THEN** the backend rejects the update with a client error and does not change the profile

#### Scenario: Inactive or unauthorized sessions cannot edit the profile

- **WHEN** an inactive internal user, a `Cliente` session, a visitor or an unauthenticated caller requests a profile update
- **THEN** the backend denies access before writing any user record

### Requirement: Internal users can change their own password securely

The system SHALL allow an active internal user to change their own password only after
validating the current password. The new password SHALL contain at least eight characters
with at least one letter and one digit, SHALL match the confirmation field and SHALL differ
from the current password. A wrong current password, divergent confirmation or invalid new
password SHALL be rejected with a client error and SHALL NOT change the stored password. The
operation SHALL update only the authenticated user's password and SHALL NOT return the
password, hash or token. Existing authentication tokens are not globally revoked by this
operation.

#### Scenario: User changes their password with the current password

- **WHEN** an active internal user submits the correct current password, a valid new password and matching confirmation
- **THEN** the backend stores the new password and confirms success without returning credentials

#### Scenario: Wrong current password is rejected

- **WHEN** an active internal user submits an incorrect current password
- **THEN** the backend rejects the change and the stored password remains unchanged

#### Scenario: Invalid new password is rejected

- **WHEN** the new password is shorter than eight characters, lacks a letter or digit, equals the current password or does not match the confirmation
- **THEN** the backend rejects the change without writing

#### Scenario: Another user's password cannot be changed

- **WHEN** a user attempts to submit a target user identifier or another user's credentials through the password operation
- **THEN** only the authenticated user's password can be affected and restricted input is rejected

### Requirement: Internal user management and profile interfaces are scoped and observable

The internal workspace SHALL provide a "Usuários" section only to active `ADMINISTRADOR` and
a "Meu perfil" view to both approved profiles. The management section SHALL list users,
offer creation and editing forms and require two-step confirmation for inactivation or
reactivation. The administrator's own role and status controls SHALL be disabled with an
explanation. The profile view SHALL update the displayed identity only after a confirmed
response and SHALL provide separate password fields. Controls SHALL be disabled while an
operation is pending. Failures SHALL keep the last confirmed data, show observable feedback
and SHALL NOT report success. Styles SHALL remain scoped to the internal workspace.

#### Scenario: Administrator manages users from the workspace

- **WHEN** an active administrator opens the "Usuários" section
- **THEN** the interface lists internal users and exposes creation, editing and two-step status actions without exposing credentials

#### Scenario: Non-administrator cannot open user management

- **WHEN** an active `FUNCIONARIO` attempts to select the "Usuários" section
- **THEN** the interface rejects the selection and does not render the administrative user list

#### Scenario: User opens and updates their profile

- **WHEN** an active internal user opens "Meu perfil" and submits valid name or email changes
- **THEN** the interface shows the confirmed identity only after the backend response and keeps the workspace session active

#### Scenario: Profile password change is observable

- **WHEN** a password change succeeds or fails
- **THEN** success clears the password fields, while failure keeps the submitted values, shows an observable message and does not claim that the password changed
