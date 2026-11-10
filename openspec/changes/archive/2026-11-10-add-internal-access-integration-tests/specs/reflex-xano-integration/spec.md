## ADDED Requirements

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
