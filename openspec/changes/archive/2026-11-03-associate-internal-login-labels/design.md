# Design — internal login labels

## Decision

Extend the shared `form_field` helper with an optional field ID. When provided, render the visible text as an HTML `<label>` with `for` referencing that ID; without it, keep the existing rendering unchanged. Supply unique IDs only to the internal email and password controls.

## Constraints

- Preserve `name="email"` and `name="password"`, input types, `required`, placeholders, and `State.submit_login`.
- Do not change existing calls to the helper or markup of other forms.
- Do not change global CSS, authentication, or Xano requests.

## Verification

Inspect the diff for both label/ID pairs and preservation of form attributes and handler. Validate the change with strict OpenSpec and `git diff --check`. No real login or remote mutation is required.
