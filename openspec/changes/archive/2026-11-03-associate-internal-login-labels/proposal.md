# Associate labels with internal login fields

## Why

The internal login audit found that the email and password controls have no programmatically associated labels. Nearby text and placeholders do not provide a persistent label association for assistive technology.

## What Changes

- Associate the visible email and password labels with their inputs using stable unique IDs.
- Preserve the existing form names, input types, required validation, handlers, authentication behavior, and presentation.

## Out of Scope

- Change authentication, sessions, authorization, payloads, or endpoints.
- Modify other forms that use the shared helper.
- Change heading hierarchy, price formatting, contrast, other screens, or mobile behavior.
- Test real accounts or modify Xano data.

## Impact

Only the internal login form in Reflex and the `internal-access` specification. No backend or data changes.
