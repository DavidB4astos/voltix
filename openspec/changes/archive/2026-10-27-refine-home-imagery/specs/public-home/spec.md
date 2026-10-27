## MODIFIED Requirements

### Requirement: Hero promoting the catalog

The public home SHALL present a premium editorial hero on the store's dark navy surface, without an eyebrow or kicker label above the heading, with a single page-level heading, a short supporting sentence, exactly one primary call-to-action labeled "Explorar produtos" leading to the existing public catalog, and a media panel. The hero media SHALL be composed only from an approved local asset from the store's assets — either a licensed photograph or a store-owned generated image — or, when that asset does not suit the composition, a store-owned graphic panel built from the store's visual tokens. The hero SHALL NOT reference external image URLs, SHALL NOT introduce promotions, prices, ratings, or commercial claims that do not exist in the store, and SHALL keep the call-to-action's current route and access behavior.

**Implementation:** The hero SHALL prioritize displaying a store-owned generated editorial image (`vtx-home-workspace-v2.webp`) with its provenance statement ("Cenário ilustrativo gerado por IA; os equipamentos não representam produtos específicos."). The store-owned graphic panel SHALL be used only as fallback when the photograph is unavailable or unsuitable for the composition.

#### Scenario: Visitor interacts with the hero
- **WHEN** a visitor activates "Explorar produtos" in the hero
- **THEN** the system navigates to the existing public catalog page

#### Scenario: Home renders on a narrow viewport
- **WHEN** the home is viewed at mobile width
- **THEN** the hero stacks heading, supporting sentence, call-to-action and media without horizontal overflow, keeping all of them reachable and readable

#### Scenario: Hero media uses only local approved assets
- **WHEN** the hero renders its media panel
- **THEN** the media is an approved local asset (a licensed photograph or a store-owned generated image) or a store-owned graphic panel, and no external image URL is requested

#### Scenario: Local hero asset does not suit the composition
- **WHEN** the approved local asset cannot be used without cropping or distortion that misrepresents it
- **THEN** the hero renders the store-owned graphic panel instead of an external or fabricated image

#### Scenario: Hero is rendered without an eyebrow
- **WHEN** the hero renders its heading
- **THEN** no eyebrow, kicker or pill label is displayed above the level-one heading

#### Scenario: Hero displays editorial photograph with provenance
- **WHEN** the hero renders with the local generated editorial image
- **THEN** the generated editorial scenery is displayed without representing catalog SKUs
- **AND** a visible provenance statement "Cenário ilustrativo gerado por IA; os equipamentos não representam produtos específicos." is shown without requiring interaction
- **AND** no fabricated author, license or source is displayed

---

### Requirement: Editorial context section with approved photography

The public home SHALL include one editorial section that presents an approved local photograph from the store's assets, a short heading, a short supporting sentence, and at most one call-to-action leading to an existing public route. The accompanying copy SHALL describe the photograph truthfully and SHALL NOT attribute a product, offer, setup or service to the image that it does not show. The section SHALL display the image credit. If no approved photograph is available, the section SHALL be omitted entirely.

**Implementation:** The editorial section SHALL use `vtx-editorial-mx-master-3s.jpg` (Mouse Logitech MX Master 3S) with the heading "Precisão em cada detalhe", supporting copy describing the premium equipment, and visible credit "Logitech MX Master 3S HS17.jpg by Hayden Schiff, CC BY 4.0, via Wikimedia Commons" without requiring interaction.

#### Scenario: Visitor views the editorial section
- **WHEN** the public home renders the editorial section
- **THEN** it shows an approved local photograph (`vtx-editorial-mx-master-3s.jpg`)
- **AND** its credit (author: Hayden Schiff, license: CC BY 4.0, source: Wikimedia Commons) is visible without interaction
- **AND** a short heading "Precisão em cada detalhe" describes the content
- **AND** a supporting sentence describes the premium equipment truthfully
- **AND** at most one call-to-action leads to `/catalogo`

#### Scenario: No approved editorial photograph is available
- **WHEN** the store has no approved local photograph for the editorial section
- **THEN** the home omits the section instead of rendering a placeholder or an unlicensed image
