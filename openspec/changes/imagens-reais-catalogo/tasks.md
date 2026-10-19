## Tasks

### 1. Research & licensing (approved update)
- [x] 1.1 Compile definitive list of exact models for VTX-DEMO-001..020 (manufacturer part numbers) and confirm correspondence to current product names/SKUs in catalog.
- [x] 1.2 Search manufacturers, distributors, specialty retailers, and marketplaces for product images. Verify exact model match (including variant/capacity/version) with at least two references where possible. No AI-generated images, similar products, or different versions.
- [x] 1.3 For each candidate image, register source URL and usage conditions. Publicly accessible does not mean authorized for reproduction. Download only images whose use is authorized or properly licensed.
- [x] 1.4 If in doubt about identity or permission, keep placeholder and record the pending item.
- [x] 1.5 Record findings: verified count, usable count, pending count with reasons. (3 approved: VTX-DEMO-003 CC BY-SA 4.0, VTX-DEMO-004 CC BY 4.0, VTX-DEMO-015 CC0; 17 pending with reasons in `assets/demo/manifest.json`.)

### 2. Define mapping & asset structure
- [x] 2.1 Create `assets/demo/` (or `assets/products/demo/`) directory convention in codebase; document path.
- [x] 2.2 Define `DEMO_IMAGE_MAP` (SKU ? local asset path/filename) covering all 20 SKUs with placeholders for filenames to be added after approval/licensing.
- [x] 2.3 Ensure mapping only affects SKUs starting with `VTX-DEMO-`; non-demo products unaffected.

### 3. Implement frontend image resolution (minimal)
- [x] 3.1 Add helper `resolve_demo_image(sku: str, existing_image_url: str) -> str` in `voltix/voltix.py` that returns local asset path if mapped for demo SKU and exists conceptually; else returns `existing_image_url`.
- [x] 3.2 Apply resolution in Home render paths where product images are shown (cards using `State.public_products` or featured items).
- [x] 3.3 Apply resolution in public catalog cards/list and detail view (`State.public_selected_product`).
- [x] 3.4 Update `rx.image` src usage to use resolved value; preserve placeholder behavior when result is empty/invalid.
- [x] 3.5 Maintain existing behavior for non-demo SKUs.

### 4. Presentation & responsiveness
- [x] 4.1 Verify image rendering is responsive (object-fit/aspect ratio) consistent with current card/detail styles.
- [x] 4.2 Ensure no layout shifts; preserve existing spacing/radii per visual-interface.
- [x] 4.3 Handle missing local assets gracefully (fallback to existing behavior).

### 5. Validation & testing
- [x] 5.1 Verify Home, catalog, detail render with mapping (conceptually) without breaking existing pages.
- [x] 5.2 Confirm non-demo products unchanged (regression check).
- [x] 5.3 All existing unit tests still pass (123/123 context).
- [x] 5.4 OpenSpec validate passes (`openspec validate --all`).
- [x] 5.5 Manual smoke test of pages.

### 6. Documentation & handoff
- [x] 6.1 Document mapping file location and process for adding approved images.
- [x] 6.2 Record licensing decisions and approved sources.
- [x] 6.3 Update relevant docs if needed (minimal).

### Notes
- Approach change: automatic image research/download abandoned. The maintainer adds images manually under `assets/demo/`.
- Manual addition: drop `vtx-demo-NNN.<ext>` (supported: `.png`, `.jpg`, `.jpeg`, `.webp`) into `assets/demo/`; the resolver detects the extension automatically. No mapping edit needed.
- Resolver: exact SKU match first; when the public listing has no SKU, an explicit full-name → SKU map (`DEMO_NAME_TO_SKU`) is used with exact matching only. Placeholder preserved when no asset exists.
- No Xano/backend changes. Only VTX-DEMO-* affected.
- Evidence of previous Wikimedia Commons search and licensing research recorded in `assets/demo/manifest.json` (historical).

### Conclusion (2026-10-19)
- **Implementation complete.** The image infrastructure (resolver, extension auto-detection, name fallback, Home/catalog/detail wiring, tests) is done and verified. Verified in the browser: Home and catalog cards and product details show the correct images for VTX-DEMO-003/004/015, and pending demo SKUs keep the placeholder.
- **The 17 remaining photographs are a CONTENT pending item, not an implementation pending item.** Nothing in the code needs to change to add them: dropping `vtx-demo-NNN.<ext>` into `assets/demo/` is sufficient. They remain pending only because no properly licensed exact-model image has been selected yet (see `assets/demo/manifest.json`).
- **Local static storage is a PROVISIONAL solution**, subject to confirmation from the professor/instructor on whether persistence in the backend/database is required. If backend/DB persistence becomes mandatory, this local-asset approach would need to be revisited in a separate, approved change.
- Tests: `tests/test_demo_images.py` green (suite 138/138). OpenSpec validation passes.
