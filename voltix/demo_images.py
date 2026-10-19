import os

DEMO_ASSETS_DIR = os.path.join("assets", "demo")
DEMO_ASSET_URL_PREFIX = "/demo/"

DEMO_SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")


def _demo_asset_filename(sku: str) -> str | None:
    """Retorna o nome do arquivo de imagem demo para um SKU, se existir em disco.

    Procura por vtx-demo-NNN com qualquer extensão suportada, na ordem de
    DEMO_SUPPORTED_EXTENSIONS.
    """
    if not sku or not sku.startswith("VTX-DEMO-"):
        return None
    for ext in DEMO_SUPPORTED_EXTENSIONS:
        filename = f"vtx-demo-{sku.removeprefix('VTX-DEMO-')}{ext}"
        if os.path.exists(os.path.join(DEMO_ASSETS_DIR, filename)):
            return filename
    return None


DEMO_NAME_TO_SKU = {
    "Mouse Logitech G203 LIGHTSYNC": "VTX-DEMO-001",
    "Mouse Logitech M90": "VTX-DEMO-002",
    "Teclado Logitech K120": "VTX-DEMO-003",
    "Mouse Logitech MX Master 3S": "VTX-DEMO-004",
    "Headset HyperX Cloud II": "VTX-DEMO-005",
    "Headset HyperX Cloud Stinger 2": "VTX-DEMO-006",
    "Webcam Logitech C920 HD Pro": "VTX-DEMO-007",
    "Microfone HyperX SoloCast": "VTX-DEMO-008",
    "SSD Kingston A400 480GB": "VTX-DEMO-009",
    "SSD Kingston NV2 1TB": "VTX-DEMO-010",
    "SSD Samsung 870 EVO 500GB": "VTX-DEMO-011",
    "SSD WD Blue SN580 1TB": "VTX-DEMO-012",
    "Mem\u00f3ria Kingston FURY Beast DDR4 16GB 3200MHz": "VTX-DEMO-013",
    "Processador AMD Ryzen 5 5600": "VTX-DEMO-014",
    "Processador Intel Core i5-12400F": "VTX-DEMO-015",
    "Placa de v\u00eddeo ASUS Dual GeForce RTX 4060 8GB": "VTX-DEMO-016",
    "Roteador TP-Link Archer C6": "VTX-DEMO-017",
    "Adaptador USB Wi-Fi TP-Link Archer T3U": "VTX-DEMO-018",
    "Monitor LG 24MP400-B": "VTX-DEMO-019",
    "Monitor Samsung T350 24 polegadas": "VTX-DEMO-020",
}


def resolve_demo_image(sku: str, existing_image_url: str) -> str:
    filename = _demo_asset_filename(sku)
    if filename:
        return f"{DEMO_ASSET_URL_PREFIX}{filename}"
    return existing_image_url


def resolve_demo_image_named(
    name: str,
    sku: str,
    existing_image_url: str,
) -> str:
    if sku and sku.startswith("VTX-DEMO-"):
        return resolve_demo_image(sku, existing_image_url)
    demo_sku = DEMO_NAME_TO_SKU.get(name)
    if demo_sku:
        return resolve_demo_image(demo_sku, existing_image_url)
    return existing_image_url
