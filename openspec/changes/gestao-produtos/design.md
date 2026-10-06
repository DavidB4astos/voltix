## Context

See `proposal.md` for motivation and scope. The existing Reflex application keeps the internal bearer token in server-side State, makes Xano requests from Python, and has administrator-guarded Category and Brand endpoints. Xano currently contains Categoria and Marca but no Produto or VariacaoProduto structures or operations. The Domain Model requires each product to reference one category and one brand and to have at least one variation.

## Goals / Non-Goals

**Goals:**

- Add the smallest persisted product aggregate that always includes one or more valid variations.
- Reuse the current administrator session and server-side request patterns.
- Keep domain validation and authorization authoritative in Xano.
- Reuse existing Category and Brand records without changing their management behavior.

**Non-Goals:**

- Public catalog browsing, search, shopping, orders, payments, CRM, inventory movement history, or multiple product images.
- Permanent deletion of products or variations associated with commercial history; deletion behavior for records without that history is not added by this Change.
- A dynamic technical-attribute entity or category-specific specification schema.

## Decisions

### Persist Product and VariacaoProduto as separate related Xano entities

Create one Xano table for each domain concept. Product stores the attributes defined in the Domain Model: name, description, technical specifications, main-image reference, category and brand references, status, and audit timestamps. Variation stores its product reference, the Domain Model's name-or-description attribute, required globally unique SKU, positive price, quantity greater than or equal to zero, status, and audit timestamps. New products and variations start `ATIVO`, following the established Category/Brand creation pattern. This keeps price, SKU, and quantity on the sellable variation as required by the Domain Model; putting those fields on Product was rejected. Do not introduce extra mandatory-field rules for product name, description, or technical specifications, or an integer constraint for available quantity.

Product creation accepts its initial one-or-more variations as part of one protected backend operation. Validate the complete request, referenced active category and brand, SKU uniqueness, and all variation values before persisting the aggregate. The operation must not leave a product with no variation on failure; use Xano's supported transaction/rollback behavior or a narrowly scoped compensation for a partial creation that has no historical references. Do not add a draft state or allow incomplete products.

### Store technical specifications directly on Product and image in Xano storage

Store technical specifications directly on Product; a dynamic key/value model was rejected because it introduces an entity the Domain Model explicitly excludes. Store at most one optional primary image using Xano's native file storage and keep its returned file reference on Product; external image URLs and an image gallery are out of scope. Upload and any image-reference update must remain mediated by the Reflex State/Python layer.

### Reuse Category and Brand, with active-only new associations

Use the existing protected Category and Brand list operations when populating product forms. Only active records are selectable for new products or reassignments. Existing relationships remain intact and visible with their current inactive status if a referenced record is inactivated later; no automatic relationship removal occurs. Xano rechecks status at write time to prevent stale UI data from bypassing the rule. Supporting only active references for new associations avoids assigning newly managed products to unavailable catalog classifications.

### Enforce authorization and domain constraints in Xano

Every list and mutation endpoint for Product and Variation requires a valid Xano session and rechecks the authenticated `user` record for `role = ADMINISTRADOR` and `status = ATIVO` before accessing product data. The backend enforces required product relationships, at least one variation at aggregate creation, allowed statuses, global SKU uniqueness (including inactive variations), price greater than zero, and quantity greater than or equal to zero. UI visibility and State checks are usability measures, not authorization controls.

### Mediate all Xano calls through Reflex State/Python

The flow is `Interface Reflex -> State/lógica Python -> Xano`. State uses the existing server-side request helper pattern and keeps the bearer token backend-only. Configure Xano collection and image-upload destinations through environment configuration, fail explicitly when required configuration is missing, and do not put secrets or private destinations in versioned code. Browser code does not make direct HTTP calls to Xano.

### Keep status changes separate from edits and preserve commercial history

Provide explicit status transitions for Product and Variation, preserving records and relationships where required by the Domain Model's commercial-history rules. Editing product attributes, associations, image, or variation attributes does not implicitly change status. This Change does not add a permanent-deletion workflow; in particular, records associated with commercial history must be preserved. Product status does not trigger public-sale behavior in this Change.

## Risks / Trade-offs

- [The aggregate requires multiple persisted records, and a partial failure could violate the required-variation rule] -> Validate all inputs before writes, use Xano-supported atomicity or safe compensation, and test that failed aggregate creation leaves no incomplete product.
- [A Category or Brand can become inactive after a form is loaded] -> Revalidate references in Xano at mutation time; keep and display already existing inactive relationships.
- [SKU uniqueness can race across concurrent requests] -> Enforce uniqueness at persistence level as well as in endpoint validation, including inactive records; return a clear conflict without changing existing data.
- [Native image upload can succeed while a later product save fails, leaving an unused file] -> Keep image optional, report upload/save failures distinctly, and limit cleanup to the newly uploaded unreferenced file where Xano supports safe cleanup; never overwrite a persisted reference on failed save.
- [Administrative status changes do not implement the future storefront's availability rules] -> Keep this Change limited to maintaining status and do not add catalog or purchasing behavior.

## Migration Plan

1. Add Produto and VariacaoProduto schemas and indexes in Xano, without altering Categoria, Marca, user, or customer data.
2. Add administrator-authorized list and mutation operations, including aggregate creation and image-reference handling; validate backend constraints.
3. Add State/Python integration and the administrator-only Reflex management UI.
4. Verify allowed and rejected operations, persistence after reload, file upload behavior, domain rules, and failure handling before enabling the UI.
5. Roll back by disabling the new endpoints and removing the associated interface/configuration. Preserve any products and variations already created; do not automatically delete domain data.

## Open Questions

None.
