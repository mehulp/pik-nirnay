# Pik Nirnay — C2 Crop / Crop-Option Domain Model

**Project:** Pik Nirnay / पीक निर्णय  
**Workstream:** C2 — CropProfile  
**Version:** V0.2 — reviewed  
**Status:** READY TO FREEZE FOR V1  
**Scope:** Static crop and cropping-system reference data for Dharashiv Kharif V1  
**Depends on:** A1 V2, A3 V3, A4 V0.2, Evidence Register V0.2, C1 V0.2

---

## 1. Review conclusion

C2 V0.1 had the right central idea:

```text
biological crop != decision option
```

The review keeps that split but makes four important changes:

1. `CropDefinition` is reduced to **identity/taxonomy metadata only**.
2. `CropOptionId` values are made explicitly distinct from `CropId` values.
3. Product-role metadata is labelled as **product metadata**, not agronomic truth.
4. A versioned/scoped `CropCatalog` is introduced for reproducibility.

The reviewed hierarchy is:

```text
CropDefinition
        ↓
CropOptionProfile
        ↓
CropCatalog
```

---

# 2. Why two domain levels are necessary

An atomic crop is not the same thing as a crop/cropping-system option.

Examples:

```text
CropId.SOYBEAN
```

means the biological/agricultural crop identity.

```text
CropOptionId.SOYBEAN_MONOCROP
```

means the V1 decision option "grow Soybean as a sole crop."

Likewise:

```text
CropOptionId.SOYBEAN_PIGEONPEA_INTERCROP
```

is a first-class cropping system.

The later decision engine evaluates **CropOptionProfile**, not `CropDefinition`.

---

# 3. Atomic crop IDs

```text
CropId
    SOYBEAN
    BLACK_GRAM
    PIGEONPEA
    PEARL_MILLET
```

Only crops required by active V1 decision options belong here.

Do not add every crop named in an evidence source merely for completeness.

---

# 4. CropDefinition

`CropDefinition` should contain identity-level metadata only.

Recommended structure:

```text
CropDefinition
    crop_id
    display_name_key
    alias_keys[]
```

Example:

```text
crop_id = BLACK_GRAM
display_name_key = "crop.black_gram.name"
alias_keys = [
    "crop.black_gram.alias.udid",
    "crop.black_gram.alias.urad"
]
```

## Why V0.1 was changed

V0.1 put:

```text
supported_seasons
evidence_source_ids
```

on both the atomic crop and crop-option layers.

That creates two sources of truth.

A biological crop may be cultivated in multiple seasonal/agronomic contexts. What Pik Nirnay supports is a **product-option concern**, so season/evidence belongs to `CropOptionProfile` or the catalog, not the identity object.

---

# 5. CropOptionId

Use IDs that remain unambiguous even after serialization.

Recommended enum:

```text
CropOptionId
    SOYBEAN_MONOCROP
    BLACK_GRAM_MONOCROP
    PIGEONPEA_MONOCROP
    SOYBEAN_PIGEONPEA_INTERCROP
    PEARL_MILLET_MONOCROP
    PEARL_MILLET_PIGEONPEA_INTERCROP
```

Why not reuse:

```text
SOYBEAN
BLACK_GRAM
...
```

for both enums?

Strong typing distinguishes them inside Python, but JSON, logs, analytics events and database records may not.

Explicit option IDs make domain events self-explanatory.

---

# 6. CropOptionType

```text
CropOptionType
    MONOCROP
    INTERCROP
```

Mapping is explicit.

Do not derive it by parsing the ID string.

---

# 7. CropOptionProductRole

The V0.1 `CropOptionRole` concept is retained but renamed to make its status clear.

```text
CropOptionProductRole
    CORE_BASELINE
    CORE_CURRENT_CROP
    DIVERSIFICATION_SYSTEM
    CLIMATE_CONTINGENCY_CROP
    SEVERE_DELAY_CONTINGENCY_SYSTEM
```

Recommended V1 mapping:

| Option | Product role |
|---|---|
| Soybean monocrop | `CORE_BASELINE` |
| Black Gram monocrop | `CORE_CURRENT_CROP` |
| Pigeonpea monocrop | `CORE_CURRENT_CROP` |
| Soybean + Pigeonpea | `DIVERSIFICATION_SYSTEM` |
| Pearl Millet monocrop | `CLIMATE_CONTINGENCY_CROP` |
| Pearl Millet + Pigeonpea | `SEVERE_DELAY_CONTINGENCY_SYSTEM` |

## Important

This field is for:

- UX grouping,
- product analytics,
- catalog documentation.

It is **not** a candidate-selection rule.

The decision engine must never implement:

```text
if role == SEVERE_DELAY_CONTINGENCY_SYSTEM:
    recommend_on_late_date()
```

A3/A4 rules determine relevance.

---

# 8. CropOptionProfile

Recommended structure:

```text
CropOptionProfile
    option_id
    option_type
    component_crops[]
    display_name_key
    product_role
    supported_seasons[]
    evidence_source_ids[]
    status
```

Example:

```text
option_id = SOYBEAN_PIGEONPEA_INTERCROP
option_type = INTERCROP
component_crops = [SOYBEAN, PIGEONPEA]
display_name_key = "crop_option.soybean_pigeonpea.name"
product_role = DIVERSIFICATION_SYSTEM
supported_seasons = [KHARIF]
evidence_source_ids = [SRC-005, SRC-006, SRC-011, SRC-013]
status = ACTIVE_V1
```

---

# 9. CropOptionStatus

```text
CropOptionStatus
    ACTIVE_V1
    DEFERRED
    RETIRED
```

All six current profiles are `ACTIVE_V1`.

Retaining status makes future catalog evolution explicit without reusing or deleting old IDs.

---

# 10. CropCatalog

Historical replay and explainability require knowing **which reference catalog** was used.

Recommended structure:

```text
CropCatalog
    catalog_id
    version
    district_scope
    season_scope
    crop_definitions
    crop_options
```

V1:

```text
catalog_id = "dharashiv-kharif"
version = "1.0"
district_scope = DHARASHIV
season_scope = KHARIF
```

The catalog should be immutable for a given version.

If a future review changes a crop option materially:

```text
version = "1.1"
```

rather than silently changing past semantics.

Rule versions remain separate in C3.

---

# 11. V1 profile registry

## 11.1 Soybean monocrop

```text
option_id = SOYBEAN_MONOCROP
type = MONOCROP
components = [SOYBEAN]
product_role = CORE_BASELINE
season = KHARIF
status = ACTIVE_V1
```

Evidence:

```text
SRC-001
SRC-004
SRC-005
SRC-006
SRC-007
```

---

## 11.2 Black Gram / Udid monocrop

```text
option_id = BLACK_GRAM_MONOCROP
type = MONOCROP
components = [BLACK_GRAM]
product_role = CORE_CURRENT_CROP
season = KHARIF
status = ACTIVE_V1
```

Evidence:

```text
SRC-001
SRC-005
SRC-006
```

---

## 11.3 Pigeonpea / Tur monocrop

```text
option_id = PIGEONPEA_MONOCROP
type = MONOCROP
components = [PIGEONPEA]
product_role = CORE_CURRENT_CROP
season = KHARIF
status = ACTIVE_V1
```

Evidence:

```text
SRC-001
SRC-004
SRC-005
SRC-006
SRC-007
```

---

## 11.4 Soybean + Pigeonpea intercrop

```text
option_id = SOYBEAN_PIGEONPEA_INTERCROP
type = INTERCROP
components = [SOYBEAN, PIGEONPEA]
product_role = DIVERSIFICATION_SYSTEM
season = KHARIF
status = ACTIVE_V1
```

Evidence:

```text
SRC-005
SRC-006
SRC-011
SRC-013
```

Current ICAR Maharashtra guidance supports pigeonpea intercropping with soybean, while district/regional contingency evidence gives this system a late-sowing role.

### Important

C2 records only:

```text
components = [SOYBEAN, PIGEONPEA]
```

It does not infer:

- row ratio,
- main crop,
- secondary crop,
- revenue share,
- seed share,
- agronomic weighting.

Those require separately reviewed evidence.

---

## 11.5 Pearl Millet monocrop

```text
option_id = PEARL_MILLET_MONOCROP
type = MONOCROP
components = [PEARL_MILLET]
product_role = CLIMATE_CONTINGENCY_CROP
season = KHARIF
status = ACTIVE_V1
```

Evidence:

```text
SRC-001
SRC-006
SRC-007
SRC-012
```

`SRC-012` is historical regional corroboration, not current standalone farmer advice.

---

## 11.6 Pearl Millet + Pigeonpea intercrop

```text
option_id = PEARL_MILLET_PIGEONPEA_INTERCROP
type = INTERCROP
components = [PEARL_MILLET, PIGEONPEA]
product_role = SEVERE_DELAY_CONTINGENCY_SYSTEM
season = KHARIF
status = ACTIVE_V1
```

Evidence:

```text
SRC-006
SRC-013
```

The same restriction applies: composition does not imply row ratio or component weighting.

---

# 12. Component order must not carry agronomic meaning

The tuple:

```text
[SOYBEAN, PIGEONPEA]
```

must not be interpreted as:

```text
first = main crop
second = intercrop
```

Likewise:

```text
[PEARL_MILLET, PIGEONPEA]
```

does not encode dominance or planting ratio.

Current sources support these as intercropping systems, but C2 does not yet contain enough reviewed evidence to model component roles/weights safely.

If future financial/agronomic modelling needs this, add a reviewed:

```text
CroppingSystemConfiguration
```

rather than overloading `component_crops`.

---

# 13. Fields deliberately excluded

Do not put the following on static profiles.

## Crop duration

Do not use:

```text
duration_days = 120
```

Duration is variety-dependent.

## Soil suitability

Do not use:

```text
allowed_soils
preferred_soils
```

A4 makes soil applicability contextual.

## Sowing window

Do not use:

```text
normal_start
normal_end
last_sowing_date
```

A3 owns timing.

## Irrigation requirement

Do not use:

```text
requires_irrigation
```

Irrigation effects are contextual.

## Risk

Do not use:

```text
risk_score
drought_tolerance_score
failure_probability
```

No reviewed universal scoring model exists.

## Prices / profitability

Do not use:

```text
market_price
expected_profit
```

Those are dynamic later-stage data.

## Row ratio

Do not use:

```text
row_ratio
```

until reviewed agronomic configuration is introduced.

---

# 14. Phase B market integration

C2 should remain provider-independent.

Do not add:

```text
agmarknet_commodity_code
provider_market_name
```

to `CropDefinition`.

Instead:

```text
CropId
    ↓
MarketProviderMapping
    ↓
AGMARKNET / other provider
```

This is particularly important for intercropping systems because:

```text
SOYBEAN_PIGEONPEA_INTERCROP
```

has no single commodity market price.

The later financial model will need component-level market observations.

---

# 15. External/source-only alternatives

A4 sources mention options that Pik Nirnay V1 does not actively model, including:

- Niger
- fodder Sorghum
- fodder Maize
- Green Gram
- Rabi crops

Do not create active `CropOptionProfile`s merely so provenance can mention them.

Recommended lightweight provenance object:

```text
ExternalOptionReference
    canonical_key
    display_name_key?
    source_ids[]
```

Example:

```text
canonical_key = "fodder_sorghum"
source_ids = [SRC-006]
```

This lets a rule preserve:

> Source also lists fodder sorghum

without making fodder sorghum a V1 candidate.

`ExternalOptionReference` is provenance metadata, not part of the active crop catalog.

---

# 16. Registry implementation

For V1 use a version-controlled code/config registry rather than database CRUD.

Reason:

- six active profiles,
- no agronomist admin UI,
- changes should pass Git review,
- catalog version should accompany code,
- avoids premature persistence infrastructure.

Conceptually:

```python
CROP_CATALOG_V1 = CropCatalog(...)
```

The registry should be immutable after startup.

---

# 17. Suggested Python/Pydantic shape

Illustrative:

```python
class CropDefinition(BaseModel):
    crop_id: CropId
    display_name_key: str
    alias_keys: tuple[str, ...] = ()
```

```python
class CropOptionProfile(BaseModel):
    option_id: CropOptionId
    option_type: CropOptionType
    component_crops: tuple[CropId, ...]
    display_name_key: str
    product_role: CropOptionProductRole
    supported_seasons: tuple[Season, ...]
    evidence_source_ids: tuple[str, ...]
    status: CropOptionStatus
```

```python
class CropCatalog(BaseModel):
    catalog_id: str
    version: str
    district_scope: District
    season_scope: Season
    crop_definitions: dict[CropId, CropDefinition]
    crop_options: dict[CropOptionId, CropOptionProfile]
```

Use immutable/frozen Pydantic models if compatible with the project's Pydantic version.

---

# 18. Validation invariants

C2 may enforce structural invariants:

### Monocrop

```text
option_type = MONOCROP
=> len(component_crops) == 1
```

### Intercrop

```text
option_type = INTERCROP
=> len(component_crops) >= 2
```

### Component validity

Every component must exist in `crop_definitions`.

### V1 scope

Every active V1 option must support:

```text
KHARIF
```

### Evidence

Every active V1 option must have at least one canonical `SRC-*` evidence ID.

### Identity

All option IDs and crop IDs must be unique inside their respective registries.

---

# 19. Invariants C2 must NOT enforce

Do not validate:

```text
SOYBEAN must be component 1
PIGEONPEA must be component 2
Bajra+Tur must have an exact row ratio
Soybean+Tur is only valid after July date X
Bajra only valid on shallow soil
```

Those are agronomic/context rules outside C2.

---

# 20. Candidate selection remains downstream

C2 answers:

> Which options does this catalog understand?

It does not answer:

> Which option is relevant for this assessment?

Pipeline:

```text
C1 AssessmentContext
        +
C2 CropCatalog
        ↓
A3 timing rules
        ↓
A4 contingency rules
        ↓
candidate evaluations
        ↓
later climate / financial comparison
```

---

# 21. Suggested tests

Claude should eventually test:

1. catalog ID/version/scope are stable,
2. exactly four atomic V1 crops exist,
3. exactly six active V1 options exist,
4. serialized crop IDs differ clearly from option IDs,
5. four monocrop profiles have one component each,
6. two intercrop profiles contain the correct atomic crops,
7. component order is not used to derive a role,
8. every component resolves to a valid crop definition,
9. every active option supports Kharif,
10. every active option has canonical source IDs,
11. active catalog is immutable,
12. source-only alternatives are absent from active candidates,
13. profiles contain no soil rules, sowing dates, market prices or risk scores,
14. catalog version survives serialization/deserialization.

---

# 22. Review decisions

| Question | Frozen V1 decision |
|---|---|
| One generic crop object? | **No** — keep `CropDefinition` + `CropOptionProfile` |
| Duplicate season/evidence metadata on CropDefinition? | **No** |
| Reuse `SOYBEAN` as both crop ID and option ID? | **No** — use explicit `*_MONOCROP` / `*_INTERCROP` IDs |
| Keep product role? | **Yes**, renamed `CropOptionProductRole`; never used as agronomic rule |
| Database registry? | **No** — immutable code/config registry for V1 |
| Catalog version? | **Yes** — required for audit/replay |
| Fixed duration? | **No** |
| Intercrop row ratio/main-crop semantics? | **Deferred** |
| Market-provider code inside core crop model? | **No** |
| Structured provenance for unsupported source alternatives? | **Yes**, via lightweight `ExternalOptionReference` |

---

# 23. C2 freeze decision

**Status: `READY_TO_FREEZE` for V1.**

The reviewed model cleanly separates:

```text
crop identity
        ↓
supported decision option
        ↓
versioned Dharashiv Kharif catalog
```

while leaving timing, soil suitability, contingency actions, market mapping and risk evaluation in their proper downstream layers.
