## Context

See [proposal.md](./proposal.md) and [specs/visual-interface/spec.md](./specs/visual-interface/spec.md). The app is a single Reflex module, `voltix/voltix.py`, with routes for internal access/management, public catalog, customer account, cart, checkout, and order history/details. Most screens independently compose `rx.container`, `rx.vstack`/`rx.hstack`, cards, forms, buttons, and raw spacing/border styles. `rxconfig.py` already enables Tailwind v4 and Radix Themes; no visual assets exist beyond the favicon.

## Goals / Non-Goals

**Goals:**

- Establish a compact design token set and a small group of shared presentation components.
- Apply it across the existing customer and internal routes, including responsive behavior and existing feedback states.
- Preserve the current State/data/API flows and existing security boundaries.

**Non-Goals:**

- Change route structure, page content rules, customer or internal permissions, or business outcomes.
- Add product or CRM functionality, real payment/shipping services, external UI packages, or new backend contracts.
- Redesign data models or replace the established Reflex/Tailwind/Radix stack.

## Decisions

### Define a restrained Voltix token palette

Use a deep navy base (`#102A43`), electric-cyan accent (`#00B8D9`), light page surfaces (`#F5F8FC` and white cards), and slate text/borders, with distinct semantic success, warning, and error treatments. Centralize repeated colors, spacing, radii, and shadows in shared theme/style definitions rather than scattering new literals across pages. Verify contrast for text and controls, adjusting foregrounds where necessary.

Alternative considered: dark-first pages or a broad multicolor neon palette. Rejected because the user selected premium technology with navy, electric cyan, and light surfaces, and a restrained palette keeps storefront and administration legible.

### Reuse simple Reflex presentation helpers

Extract only repeated structures used across multiple routes, such as the site header/footer, constrained page shell, section heading, surface/card wrapper, and shared button/feedback treatment. Keep existing page-specific forms and event handlers intact; prefer native Reflex/Radix/Tailwind capabilities already installed.

Alternative considered: introduce a new component framework, design-system package, or deep component hierarchy. Rejected as unnecessary complexity for the single-module school project.

### Keep customer and internal navigation contexts distinct

Use a shared brand treatment while supplying each existing route group with its current appropriate links. The current `/` route is internal login/access plus role-gated administration, while `/catalogo` is the public storefront; do not silently repurpose either route as a new landing experience.

Alternative considered: add or repurpose a public marketing home page. Rejected because that would expand route/product behavior beyond a visual refresh.

### Make layouts responsive through intrinsic and breakpoint-aware composition

Use existing responsive props/utilities and wrapping/grid behavior so product cards, forms, order summaries, and administrative lists reflow on mobile, tablet, and desktop. Avoid fixed page widths and preserve every current field, action, and message.

Alternative considered: maintain separate desktop and mobile page implementations. Rejected because shared responsive components reduce duplication and visual drift.

### Preserve all State and authorization behavior

Treat page State expressions, event handlers, route registration, and authorization conditions as behavior contracts: move or wrap presentation without changing them. In particular, role gates in internal management and customer-owned checkout/order flows remain as-is.

Alternative considered: simplify screens by removing or relocating actions and conditionally rendered content. Rejected because this Change is presentation-only.

## Risks / Trade-offs

- [Refactoring a large single Reflex module can accidentally change State event wiring] -> Make presentation-only edits in small page groups and retain existing event/property expressions.
- [Aesthetic colors may reduce contrast or status clarity] -> Use semantic colors and verify text/control readability in both normal and focus states.
- [Responsive layouts may overflow on long text or administrative controls] -> Check representative narrow, medium, and wide viewports, including long labels and wrapped action rows.
- [No current product photography or brand asset library is available] -> Establish the system with existing data and layout treatment; do not invent product imagery or add external assets.

## Migration Plan

1. Add shared visual tokens and base header/footer/page-shell helpers without touching State or route logic.
2. Apply the shared presentation to the public catalog and product details, then account and purchase-flow pages.
3. Apply the same system to internal access and existing administrator management components.
4. Validate Reflex compilation and existing automated behavior tests; visually inspect desktop, tablet, and narrow mobile layouts.
5. Roll back individual presentation changes if they affect existing navigation, actions, or authorization; no data/API migration is required.
