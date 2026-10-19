## Design

### Problem statement recap
Display real product photographs (no AI generation) for the 20 demo SKUs VTX-DEMO-* on Home, public catalog, and product detail pages. Xano Free image upload returns 403; serve from local static assets in Reflex without changing backend/Xano, prices/inventory/records. Preserve placeholders when missing; never affect non-demo products.

### Solution
Minimal SKU-based image resolution layer in the frontend (Reflex) mapping VTX-DEMO-* SKUs to local static asset paths (served from Reflex assets/). For demo SKUs, prefer local asset if present; otherwise fall back to existing `image_url` flow (from Xano public image endpoint). Apply mapping at render sites (product cards on Home/catalog, and detail page) without changing data models, API calls, or Xano content.

### Image mapping (by SKU)
Curated mapping for the 20 demo SKUs VTX-DEMO-001..020. Keys are SKUs. The resolver detects the local asset automatically: for a given demo SKU it probes `assets/demo/vtx-demo-NNN` with the supported extensions `.png`, `.jpg`, `.jpeg`, `.webp` (in that order) and returns `/demo/vtx-demo-NNN.<ext>` for the first file that exists. The mapping and asset directory are implemented in `voltix/demo_images.py` and `assets/demo/`.

Product list:
1. VTX-DEMO-001 - Mouse Logitech G203 LIGHTSYNC
2. VTX-DEMO-002 - Mouse Logitech M90
3. VTX-DEMO-003 - Teclado Logitech K120
4. VTX-DEMO-004 - Mouse Logitech MX Master 3S
5. VTX-DEMO-005 - Headset HyperX Cloud II
6. VTX-DEMO-006 - Headset HyperX Cloud Stinger 2
7. VTX-DEMO-007 - Webcam Logitech C920 HD Pro
8. VTX-DEMO-008 - Microfone HyperX SoloCast
9. VTX-DEMO-009 - SSD Kingston A400 480GB
10. VTX-DEMO-010 - SSD Kingston NV2 1TB
11. VTX-DEMO-011 - SSD Samsung 870 EVO 500GB
12. VTX-DEMO-012 - SSD WD Blue SN580 1TB
13. VTX-DEMO-013 - Memoria Kingston FURY Beast DDR4 16GB 3200MHz
14. VTX-DEMO-014 - Processador AMD Ryzen 5 5600
15. VTX-DEMO-015 - Processador Intel Core i5-12400F
16. VTX-DEMO-016 - Placa de video ASUS Dual GeForce RTX 4060 8GB
17. VTX-DEMO-017 - Roteador TP-Link Archer C6
18. VTX-DEMO-018 - Adaptador USB Wi-Fi TP-Link Archer T3U
19. VTX-DEMO-019 - Monitor LG 24MP400-B
20. VTX-DEMO-020 - Monitor Samsung T350 24 polegadas

### Research criteria (superseded)
Automatic image research and download were dropped. Images for `assets/demo/` are added manually by the maintainer. The criteria below are kept as historical context and still apply to any image the maintainer adds:
- Sources: manufacturers, distributors, specialty retailers, and marketplaces. Not limited to Wikimedia Commons or manufacturer press kits.
- Exact model match required, including variant, capacity, or version when applicable.
- No AI-generated images, similar products, or different versions.
- Verify model name and code with at least two references where possible.
- Register source URL and usage conditions for each image. Publicly accessible does not mean authorized for reproduction.
- Use only images whose use is authorized or properly licensed.
- If in doubt about identity or permission, keep placeholder.

### Asset storage (Reflex)
Local images under `assets/demo/`, named `vtx-demo-NNN.<ext>` with a supported extension (`.png`, `.jpg`, `.jpeg`, `.webp`), served by Reflex 0.9.12 at `/demo/vtx-demo-NNN.<ext>`. Directory and resolver already implemented.

### Provisionality of local storage
Storing images as local static assets is a **provisional** solution. It is subject to confirmation from the professor/instructor on whether image persistence in the backend/database is required. The current approach is deliberate and documented here because image upload on Xano Free returns 403 and no backend/DB change is authorized for this change. If backend/DB persistence becomes mandatory, migrating the demo images would require a separate, approved change.

### Implementation status
The image infrastructure is **complete**: resolver with extension auto-detection, exact-name fallback, wiring in `_fetch_public_products` and `load_public_product_details`, and focused tests. Only 3 of the 20 demo products have an image so far; the remaining 17 are a **content pending item, not an implementation pending item** — adding a file to `assets/demo/` is enough, no code change required.

### Resolution logic (frontend)
Helper `resolve_demo_image(sku, existing_image_url)` in `voltix/demo_images.py`:
- If SKU starts with `VTX-DEMO-`: probe `assets/demo/vtx-demo-NNN.<ext>` for `.png`, `.jpg`, `.jpeg`, `.webp` (in this order); return `/demo/vtx-demo-NNN.<ext>` for the first existing file.
- Else: return `existing_image_url` unchanged (placeholder fallback).

Helper `resolve_demo_image_named(name, sku, existing_image_url)`:
- If SKU starts with `VTX-DEMO-`: resolve by SKU as above.
- Else: look up the exact product name in `DEMO_NAME_TO_SKU` (all 20 demo product names as returned by the public products endpoint) and resolve by that SKU if a local asset exists. Matching is exact — no fuzzy/partial matching.
- Else: return `existing_image_url` unchanged.

Why the name fallback exists: the public `/products` list endpoint (Xano Free) returns records without variations, so the SKU is unavailable on Home/catalog card loads (`{"image_url": null}` is all `/products/{id}/image` returns for demo products). Without a fallback, demo images would only appear on the detail view, which fetches variations and therefore has the SKU. The name lookup is a frontend-only presentation mapping; it is applied in `_fetch_public_products` and `load_public_product_details`, and it never affects products whose name is not one of the 20 demo names or whose SKU is not demo-prefixed (SKU resolution takes precedence).

Applied at render sites: Home product cards, catalog grid/cards, and product detail (`public_selected_product`). Pure/presentation-only.

Adding an image manually: drop `vtx-demo-NNN.<ext>` (NNN = three-digit demo number, e.g. `vtx-demo-007.webp`) into `assets/demo/`. No code change or mapping edit is required; the resolver picks it up by extension. A Reflex restart is only needed if the server does not hot-reload asset changes (verify in the browser; static asset additions generally do not require a restart).

### Constraints & non-goals
- No backend/Xano changes, no DB schema changes, no API contract changes.
- No changes to products, prices, stock, or records.
- Images are added manually by the maintainer; no automatic research/download.
- Preserve placeholders; never affect non-demo products.

### Risks & mitigations
- Licensing: maintainer is responsible for using only images with clear license/permission.
- Model accuracy: exact model match; if uncertain, keep placeholder.
- Asset size/perf: optimize images (JPG/WebP), responsive sizing.
- Placeholder behavior: if no local asset exists, gracefully degrade to existing behavior.

### Dependencies
- Manually added image files under `assets/demo/` (or none, keeping placeholders).
