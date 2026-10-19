## Why
The demonstration storefront needs to display real product photographs (not AI-generated) for the 20 demo products (VTX-DEMO-*) to convey credibility and professionalism. Xano Free image uploads return 403, so images are served from local static assets in Reflex, mapped by SKU, without changing backend, prices, inventory, or existing records. Placeholders are preserved when no valid image exists.

## What Changes
- Display real product photographs (no AI generation) for the 20 demo SKUs VTX-DEMO-* on Home, public catalog, and product detail pages.
- Research images from manufacturers, distributors, specialty retailers, and marketplaces. Verify exact model match (including variant/capacity/version) with at least two references where possible.
- Mandatory criteria per approved update: exact model match; no AI-generated images, similar products, or different versions; register source URL and usage conditions for each image; download only images whose use is authorized or properly licensed; if in doubt about identity or permission, keep placeholder and record the pending item.
- A publicly accessible image does not imply authorized reproduction.
- Serve demo images as local static assets in Reflex, mapping by SKU without modifying Xano/bank data.
- Create a mapping of images to SKUs VTX-DEMO-001..020 with fallback to placeholder when missing.
- Ensure responsiveness, appropriate loading behavior, and preservation of existing behavior (no changes to pricing, stock, products, or records).

## Capabilities

### Modified Capabilities
- **public-catalog**: Extend image resolution for public catalog to resolve local static images for demo SKUs VTX-DEMO-* (by SKU) with graceful fallback to existing Xano-provided `image_url`. No change to filters, ATIVO/INATIVO rules, or endpoint contracts.
- **public-home**: Resolve and display real images for demo SKUs on Home cards when present, with fallback to placeholder, without changing category/product data sourcing or eligibility rules.
- **visual-interface**: Define presentation rules for real images (responsive layout, loading, error/placeholder states) consistent with Voltix visual identity, preserving all existing behaviors.

## Impact
- Frontend Reflex (`voltix/voltix.py`) and local static assets structure (assess `assets/` per Reflex conventions). No backend/Xano/XanoScript, schema, API routes, pricing/inventory, or record changes.
- Scope limited to 20 demo SKUs VTX-DEMO-*. Non-demo products continue to use existing `image_url` flow.
- Accounts for Xano Free limitations (403 on uploads) and AP2 timeline. No image download/storage in this planning phase.

## Outcome
- **Approach superseded:** automatic image research/download was abandoned. The maintainer adds images manually under `assets/demo/`.
- **Infrastructure implemented (complete):** `voltix/demo_images.py` (`resolve_demo_image`, `resolve_demo_image_named`, `DEMO_NAME_TO_SKU`) with automatic detection of `vtx-demo-NNN` in `.png`, `.jpg`, `.jpeg`, `.webp`; applied in `_fetch_public_products` and `load_public_product_details`. Falls back to existing `image_url` when no local asset file exists. Verified in Home, catalog and details.
- **Content pending (not implementation):** 3 of 20 demo images added so far (`vtx-demo-003.jpg`, `vtx-demo-004.jpg`, `vtx-demo-015.jpg`). The remaining 17 only await a properly licensed exact-model photograph; adding one is a file drop with no code or mapping change.
- **Provisional storage:** local static assets are a provisional solution, subject to confirmation from the professor/instructor on whether backend/database persistence is required. No backend/DB/Xano change is part of this change.
- Evidence: `assets/demo/manifest.json` records licensing status per SKU.
- **Historical note:** the earlier Wikimedia Commons-only search found 0/20 under CC/public-domain terms; the two Logitech images added later are independent own-work CC photos (not Logitech Assets), and the Intel photo is CC0.
- To add images later: place `vtx-demo-NNN.<ext>` in `assets/demo/` — the resolver picks it up automatically.
