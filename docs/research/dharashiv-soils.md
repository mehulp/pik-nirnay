# Dharashiv V1 Soil Depth Model

**Project:** Pik Nirnay / पीक निर्णय  
**Workstream:** A2 — Dharashiv Soil Model  
**Status:** Revised proposed V1 baseline  
**Scope:** Rain-fed / limited-irrigation Kharif decision support in Dharashiv district

## 1. Purpose

Define the soil abstraction that Pik Nirnay V1 may use when comparing crop and cropping-system climate risk.

The model must be:

- simple enough for a farmer to self-select,
- aligned with Dharashiv/Marathwada agricultural guidance,
- useful for dry-spell decision logic,
- explicit about uncertainty,
- and narrow enough that the application does not infer unsupported soil properties.

The V1 soil input is primarily a **soil-depth / water-storage proxy**, not a soil-colour classification and not a complete soil-health diagnosis.

---

## 2. Why soil depth matters in Dharashiv

Recent PoCRA monitoring work for Dharashiv/Latur reports a high proportion of shallow soils in Dharashiv and notes that shallow soils have lower water-storage capacity and therefore sustain crops less effectively through prolonged dry spells than deeper soils.

The older ICAR-CRIDA Dharashiv/Osmanabad contingency plan also separates crop and contingency recommendations by soil depth and related rainfall situations.

So soil depth is not an arbitrary application field. It is already part of the district's contingency-planning logic.

---

## 3. Why V1 should not model soil colour

Visible soil colour can vary across fields and conditions and may appear black, dark grey, brown, reddish-brown, or mixed depending on local geology, organic matter, moisture, and other factors.

For Pik Nirnay V1, colour does not add enough decision value to justify a separate input.

The product cares more about:

- effective soil depth,
- relative water-storage capacity,
- dry-spell buffering,
- interaction with crop choice and irrigation.

Therefore V1 should ask the farmer about **soil depth**, not whether the soil is "black" or "brown."

---

## 4. Reconciling official soil-depth classifications

Different agricultural sources use different numbers of soil-depth classes.

A VNMKV soil-and-water-conservation manual uses classes such as:

| Source category | Approximate depth |
|---|---:|
| Shallow | 7.5–22.5 cm |
| Medium | 22.5–45 cm |
| Medium deep | 45–90 cm |

Other Maharashtra classifications use more granular bands.

Pik Nirnay does **not** need that level of granularity in V1.

For the prototype, several official classes are normalized into three farmer-facing depth bands plus UNKNOWN.

This is a **product normalization**, not a claim that Maharashtra officially uses only three depth categories.

---

## 5. Proposed V1 soil-depth classes

### 5.1 SHALLOW

**Marathi label:** उथळी जमीन  
**Approximate project depth:** less than 50 cm  
**Farmer-friendly cue:** मुरूम / खडक साधारण दीड फूटाच्या आत लागतो

### Climate-risk interpretation

- Low relative soil-water storage.
- Higher vulnerability to prolonged dry spells.
- Rainfall distribution is especially important.
- A crop may establish after sowing rain but experience stress if rainfall stops for an extended period.

### Decision-engine permission

The engine **may** use this class to:

- increase dry-spell exposure,
- apply shallow-soil-specific contingency rules,
- influence crop/cropping-system feasibility where the approved rule matrix explicitly distinguishes shallow soil,
- explain why a crop has greater climate exposure.

The engine must not derive a crop decision from this field alone.

---

### 5.2 MEDIUM_DEEP

**Marathi label:** मध्यम खोल जमीन  
**Approximate project depth:** 50–100 cm  
**Farmer-friendly cue:** मुरूम / खडक साधारण दीड ते तीन-सव्वातीन फूट खोल लागतो

### Climate-risk interpretation

- Moderate relative soil-water storage compared with shallow soil.
- Better dry-spell buffering than shallow soil.
- Still dependent on rainfall distribution, crop stage and irrigation availability.

### Decision-engine permission

The engine **may**:

- treat dry-spell exposure as lower than otherwise comparable shallow-soil situations,
- apply medium/deep-soil contingency rules where approved,
- use the class jointly with sowing date, irrigation and climate conditions.

---

### 5.3 DEEP

**Marathi label:** खोल जमीन  
**Approximate project depth:** greater than 100 cm  
**Farmer-friendly cue:** मुरूम / खडक साधारण तीन-सव्वातीन फूटांपेक्षा अधिक खोल

### Climate-risk interpretation

- Higher relative soil-water storage than shallow soil.
- Can sustain crops through dry periods for longer than shallow soils, all else being equal.
- Does **not** imply unlimited drought protection.

### Decision-engine permission

The engine **may**:

- reduce relative dry-spell exposure compared with shallow soil,
- apply deep-soil contingency rules,
- consider longer-duration options where supported by approved agronomic rules.

Deep soil must not automatically produce a LOW climate-risk label.

---

### 5.4 UNKNOWN

**Marathi label:** माहिती नाही  
**Meaning:** Farmer does not know the effective soil depth or is not confident selecting a class.

UNKNOWN is a valid input, not an error.

### Decision-engine behaviour

When soil depth is UNKNOWN:

- do not fabricate or infer a depth from district averages,
- do not apply soil-specific hard exclusions,
- run rules that do not depend on soil depth,
- clearly state that the assessment is less specific because soil depth is unknown,
- retain the option for the user to update the answer later.

The district's dominant soil category must **not** be silently substituted for an individual field.

---

## 6. Internal enum

Recommended software representation:

```text
SoilDepthClass
    SHALLOW
    MEDIUM_DEEP
    DEEP
    UNKNOWN
```

This replaces the earlier provisional enum that included `*_BLACK`.

If approved, the PRD and any earlier docs should be updated to use these names.

---

## 7. Farmer-facing question

Recommended Marathi:

> **तुमच्या शेतातील माती साधारण किती खोल आहे?**

Options:

```text
उथळी जमीन
मुरूम / खडक साधारण दीड फूटाच्या आत लागतो

मध्यम खोल जमीन
मुरूम / खडक साधारण दीड ते तीन-सव्वातीन फूट खोल लागतो

खोल जमीन
मुरूम / खडक साधारण तीन-सव्वातीन फूटांपेक्षा अधिक खोल

माहित नाही
```

Recommended English:

```text
Shallow soil
Rock/murrum is reached within roughly 1.5 ft

Medium-deep soil
Rock/murrum is reached at roughly 1.5–3.25 ft

Deep soil
Soil continues beyond roughly 3.25 ft

I don't know
```

These are prototype UX labels and should later be field-checked with local users/agronomy experts.

---

## 8. Important distinction: depth is not the whole soil

Pik Nirnay must not treat a soil-depth selection as a complete soil profile.

Soil depth alone does **not** establish:

- exact available water capacity,
- soil texture,
- drainage quality,
- pH,
- salinity,
- organic carbon,
- N/P/K or micronutrient status,
- exact current soil moisture,
- fertility,
- expected yield.

Therefore V1 must not make fertilizer or nutrient recommendations from the soil-depth field.

---

## 9. Excess-rain and drainage caution

Soil depth alone is not sufficient to estimate drainage or waterlogging risk.

Therefore:

- SHALLOW must not automatically mean "low flood risk",
- DEEP must not automatically mean "high waterlogging risk",
- the V1 engine should only use soil depth directly for dry-spell/storage-related logic unless a specific approved rule says otherwise.

If A4 later shows that excess-rain decision quality requires it, a separate field such as:

```text
DrainageCondition
    GOOD
    WATER_STANDS_AFTER_HEAVY_RAIN
    UNKNOWN
```

may be considered.

Do not add it to V1 unless the rule matrix demonstrates a clear need.

---

## 10. Relative water-storage band

For rule-engine use, the soil classes may carry an ordinal water-storage indicator:

```text
SHALLOW      -> LOW
MEDIUM_DEEP  -> MODERATE
DEEP         -> HIGH
UNKNOWN      -> UNKNOWN
```

This is intentionally **relative**, not a numeric plant-available-water measurement.

Do not convert LOW / MODERATE / HIGH into millimetres without field-specific evidence.

---

## 11. Proposed domain object

Conceptually:

```text
SoilContext
    depth_class
    source
```

Possible source values:

```text
USER_REPORTED
GIS_SUGGESTED
FIELD_MEASURED
UNKNOWN
```

For V1, most records will be:

```text
source = USER_REPORTED
```

This preserves a path for later geospatial assistance without changing the meaning of the depth class.

---

## 12. Future geospatial assistance

PoCRA GIS soil services expose village-level layers such as:

- soil depth,
- water-holding capacity,
- texture,
- organic carbon.

A future flow could be:

```text
Farmer selects village
        ↓
Pik Nirnay obtains a location-level soil-depth suggestion
        ↓
"Your area commonly has shallow soil — is this true for your field?"
        ↓
Farmer confirms / corrects
```

The system should **not** silently convert village-level mapping into field-level ground truth.

---

## 13. Decision-engine boundaries

### Soil depth MAY influence

- dry-spell exposure,
- drought-buffer interpretation,
- soil-specific crop/cropping-system rules,
- delayed-sowing contingency rules,
- explanations shown on the risk card.

### Soil depth MUST NOT independently determine

- the "best crop",
- expected yield,
- expected profit,
- fertilizer dose,
- disease risk,
- exact soil moisture,
- waterlogging probability,
- crop-failure probability.

The engine must combine soil depth with other approved variables:

```text
soil depth
    +
sowing date
    +
irrigation availability
    +
weather/climate condition
    +
crop/cropping system
```

---

## 14. Example future rule interaction

Illustrative structure only; this is **not yet an approved A4 rule**:

```text
IF
    soil_depth = SHALLOW
AND irrigation = RAINFED
AND prolonged_dry_spell_risk = HIGH

THEN
    increase dry_spell_exposure for sensitive crop options

EXPLANATION
    "Your field has shallow soil and no protective irrigation,
     so it can store less water through a long break in rainfall."
```

A2 defines the meaning of `SHALLOW`.

A4 must define whether and how that condition changes each crop's risk.

---

## 15. Evidence and provenance

### Primary district evidence

**ICAR-CRIDA — Agriculture Contingency Plan, District Osmanabad (Dharashiv)**  
The plan reports major soil-depth categories for the district and explicitly separates shallow-soil and medium/deep-soil farming situations in contingency recommendations.

Source:  
https://www.icar-crida.res.in/cp-2012/statewiseplans/Maharastra(Pdf)/MAU,%20Parbhani/Maharashtra%2030-Osmanabad-%2031-12-2011.pdf

### Recent Dharashiv evidence

**PoCRA — Concurrent Monitoring Round X Report (2024)**  
Reports Dharashiv soil-depth distribution and notes that shallow soils have lower water-storage capacity, while deeper soils sustain crops longer during dry spells.

Source:  
https://mahapocra.gov.in/assets/docs/mne/Final_Report_SambodhiCM_PoCRA_1June2024.pdf

### Soil-depth classification reference

**VNMKV — Soil and Water Conservation Engineering Practical Manual**  
Provides depth bands including shallow, medium and medium-deep soils.

Source:  
https://coap.vnmkv.ac.in/Content/Home/assets/pdf/DepAgriEngineer/Practical-manual-ENGG-121.pdf

### Possible future soil-map assistance

**PoCRA GIS Soil Services**  
Provides village soil-map layers including soil depth, water-holding capacity and texture.

Source:  
https://gis.mahapocra.gov.in/html/soil-services/nbss-soil-advisory.html

---

## 16. Assumptions and cautions

1. The `<50 cm / 50–100 cm / >100 cm` bands are a **Pik Nirnay V1 normalization** of more granular official classifications.
2. Farmer-friendly foot equivalents are approximate.
3. Farmer self-report may be inaccurate; `UNKNOWN` remains valid.
4. Soil depth primarily informs dry-spell/storage risk in V1.
5. Soil colour is deliberately not modelled as an input.
6. Soil fertility and nutrient recommendations are outside the V1 soil model.
7. Village-level soil maps must not be treated as exact field measurements.
8. This model remains a research-prototype abstraction until validated with local agronomy expertise and farmers.

---

## 17. A2 exit criteria

A2 is complete when the product owner approves:

- four soil-depth states including UNKNOWN,
- the approximate V1 depth normalization,
- Marathi/English farmer-facing terminology,
- the decision not to model soil colour,
- the rule-engine permissions and prohibitions,
- and the decision not to infer drainage/fertility from soil depth.

**Proposed status: COMPLETE, subject to product-owner approval.**

Next dependency:

**A3 — Dharashiv Sowing Window Matrix**

A3 should define preferred, delayed and contingency sowing periods for the five A1 crop/cropping-system options.
