# Pik Nirnay — Evidence Register

**Project:** Pik Nirnay / पीक निर्णय  
**Document:** Evidence Register  
**Version:** V0.2 — reviewed  
**Review date:** 2026-09-27  
**Status:** READY WITH LIMITATIONS  
**Scope:** Dharashiv Kharif V1 domain research and contingency rules

---

## 1. Purpose

This register is the traceability layer between:

```text
Source evidence
    ↓
Research interpretation
    ↓
Product/domain rule
    ↓
Software implementation
    ↓
Tests / explanations
```

It records what each source actually supports, how Pik Nirnay interprets it, and where that interpretation remains uncertain.

A source-backed rule is not automatically field-validated advice.

---

## 2. Review findings incorporated in V0.2

The review of V0.1 produced five changes:

1. **Canonical source IDs introduced.**  
   A source now has one ID (`SRC-001`, `SRC-002`, etc.) instead of aliases such as `E-A1-04 / E-A3-03 / E-A4-03`.

2. **Pinpoint references added.**  
   Important PDF evidence now records the relevant PDF page/table/section rather than only a URL.

3. **Late-sown pearl millet evidence downgraded from “current.”**  
   The recommendation is a **2019 VNMKV research recommendation**, even though it remains visible in newer VNMKV research/accreditation material. It is useful corroboration, not current 2026 guidance.

4. **A2 numeric soil cut-offs are explicitly not frozen as agronomic truth.**  
   `SHALLOW / MEDIUM_DEEP / DEEP / UNKNOWN` is accepted as the V1 categorical model, but the provisional `<50 / 50–100 / >100 cm` cut-offs remain a **product assumption requiring later agronomy validation**.

5. **Source availability is tracked.**  
   Some VNMKV deep links are unstable even when the content remains search-indexed. A broken URL must not silently become “verified current evidence.”

---

# 3. Evidence classifications

## 3.1 Evidence scope

```text
DIRECT_CURRENT_DISTRICT
DIRECT_CURRENT_REGIONAL
DIRECT_HISTORICAL_DISTRICT
DIRECT_HISTORICAL_REGIONAL
CORROBORATING_CURRENT
CONTEXT_ONLY
PRODUCT_DERIVED
CONFLICTING
```

## 3.2 Review status

```text
VERIFIED
VERIFIED_WITH_LIMITATION
REVIEW_REQUIRED
UNSTABLE_SOURCE
SUPERSEDED
DEFERRED
```

## 3.3 Source access status

```text
ACCESSIBLE
ACCESSIBLE_VIA_INDEX
UNSTABLE
UNAVAILABLE
```

---

# 4. Canonical source register

## SRC-001 — Maharashtra Final Advance Estimates 2024–25

**Institution:** Department of Agriculture, Government of Maharashtra  
**Source type:** Official district-level agricultural statistics  
**Geography:** Maharashtra; Dharashiv row used  
**Evidence scope:** `DIRECT_CURRENT_DISTRICT`  
**Access:** `ACCESSIBLE`  
**URL:**  
https://krishi.maharashtra.gov.in/Site/Upload/GR/DISTRICTWISE%20APY-2024-25.pdf

### Pinpoints

- PDF page 1: Kharif cereals — Dharashiv row.
- PDF page 2: Tur, Mung, Udid — Dharashiv row.
- PDF page 3: Kharif Soybean — Dharashiv row.
- PDF page 4: Rabi Jowar — Dharashiv row.

### Claims used

The source reports area in `"00" ha`.

Converted Dharashiv areas:

- Soybean: `4637.26 × 100 = 463,726 ha`
- Udid: `513.42 × 100 = 51,342 ha`
- Tur: `433.59 × 100 = 43,359 ha`
- Mung: `110.83 × 100 = 11,083 ha`
- Kharif Maize: `87.22 × 100 = 8,722 ha`
- Bajra: `12.57 × 100 = 1,257 ha`
- Kharif Jowar: `10.69 × 100 = 1,069 ha`
- Rabi Jowar: `1727.44 × 100 = 172,744 ha`

### Used by

- A1 crop shortlist
- Inclusion of Udid
- Deferral of Kharif Jowar
- Classification of Bajra as a contingency crop rather than a dominant current crop

### Limitation

Crop area shows present-day importance; it does not by itself establish field-level crop suitability.

### Review status

`VERIFIED`

---

## SRC-002 — PoCRA Concurrent Monitoring Round X Report

**Institution:** Project on Climate Resilient Agriculture (PoCRA), Maharashtra  
**Date:** 2024  
**Source type:** Recent monitoring / field study  
**Geography:** Dharashiv and Latur monitoring locations  
**Evidence scope:** `DIRECT_CURRENT_DISTRICT` for reported district soil table; `CONTEXT_ONLY` for study-village crop patterns  
**Access:** `ACCESSIBLE`  
**URL:**  
https://mahapocra.gov.in/assets/docs/mne/Final_Report_SambodhiCM_PoCRA_1June2024.pdf

### Pinpoint

PDF page 135, section **“Soil types and rainfall distribution patterns of the visited districts”**, Table 1 and following rainfall discussion.

### Claims used

For Dharashiv the table reports, as percentage of **total geographical area**:

- Deep black soil: 23.14%
- Medium-deep black soil: 10.72%
- Shallow black soil: 66.14%

The report states shallow soil has lower water-storage capacity and crops sustain dry spells for less time than in deep black soil.

For the selected study context it also reports:

- soybean as a major Kharif crop (about 80% cultivated area in the discussed study context),
- monsoon delay of more than 15 days in Kharif 2023,
- a 48-day deficient-rainfall period in Dharashiv from 3 August to 20 September 2023.

### Used by

- A1 soybean context
- A2 soil-depth rationale
- climate-risk problem framing
- historical replay candidate season

### Limitations

- The “about 80%” soybean statement belongs to the study context and must not be presented as district-wide official acreage.
- Village-level observations are not field-level truth for every farmer.
- The soil table percentage denominator is total geographical area, not necessarily cultivated area.

### Review status

`VERIFIED_WITH_LIMITATION`

---

## SRC-003 — VNMKV KVK Osmanabad/Dharashiv Annual Progress Report 2024

**Institution:** VNMKV / Krishi Vigyan Kendra Osmanabad (Dharashiv)  
**Source type:** Recent district extension report  
**Geography:** KVK jurisdiction in Dharashiv/Osmanabad  
**Evidence scope:** `DIRECT_CURRENT_DISTRICT`  
**Access:** `ACCESSIBLE`  
**URL:**  
https://www.vnmkv.ac.in/Content/Home/pdf/extension/KVK-APR-2024.pdf

### Pinpoint

PDF page 6, sections:

- 2.2 Agro-climatic Zone & major agro-ecological situations
- 2.3 Soil Types

### Claims used

The KVK report distinguishes district soil/agro-ecological situations including:

- deep black soils,
- medium-deep black soils,
- medium-deep to shallow soils,
- scarcity zones with roughly 500–700 mm annual rainfall,
- transition zones with roughly 700–900 mm rainfall.

### Used by

- A2 categorical soil-model corroboration
- A4 principle that Dharashiv is not one homogeneous soil/rainfall situation

### Limitation

The table supports categorical soil differences but does not establish Pik Nirnay’s provisional numeric depth thresholds.

### Review status

`VERIFIED`

---

## SRC-004 — VNMKV College of Agriculture, Dharashiv

**Institution:** VNMKV  
**Source type:** Institutional district context  
**Geography:** Dharashiv  
**Evidence scope:** `CORROBORATING_CURRENT`  
**Access:** `ACCESSIBLE`  
**URL:**  
https://coaob.vnmkv.ac.in/page.php?slug=about_us

### Claim used

Soybean and red gram/pigeonpea are identified among important district crops.

### Used by

A1 crop shortlist.

### Limitation

Not a crop-contingency or current acreage dataset.

### Review status

`VERIFIED`

---

## SRC-005 — ICAR Kharif Agro-Advisories for Farmers 2025, Maharashtra

**Institution:** Indian Council of Agricultural Research (ICAR)  
**Date:** 2025  
**Source type:** Official current state agro-advisory  
**Geography:** Maharashtra  
**Evidence scope:** `DIRECT_CURRENT_REGIONAL`  
**Access:** `ACCESSIBLE_VIA_INDEX`  
**URL:**  
https://icar.gov.in/sites/default/files/Circulars/ICAR-En-Kharif-Agro-Advisories-for-Farmers-2025.pdf

### Pinpoint

Maharashtra section, pulse-crop pages around the indexed page 147.

### Claims used

- Soybean sowing should be completed before about 15 July to reduce pest exposure.
- Pigeonpea:
  - early varieties: first fortnight of June,
  - medium/late: second fortnight of June to first fortnight of July.
- Pigeonpea + Soybean intercropping is recommended.
- One or two protective irrigations are recommended for pigeonpea where possible.
- Current Black Gram varieties are listed.

### Critical interpretation rule

The advisory says **Green Gram** sowing should follow first onset with minimum 80 mm rainfall.

Do **not** transfer that threshold to Black Gram.

### Used by

- A1
- A3
- A4

### Limitation

State-wide guidance; it does not replace Dharashiv soil/rainfall context.

### Review status

`VERIFIED_WITH_LIMITATION`

---

## SRC-006 — ICAR-CRIDA Osmanabad/Dharashiv Agriculture Contingency Plan

**Institution:** ICAR-CRIDA / then MAU (now VNMKV)  
**Date:** 2011-era district plan  
**Source type:** Detailed district contingency plan  
**Geography:** Osmanabad, now Dharashiv  
**Evidence scope:** `DIRECT_HISTORICAL_DISTRICT`  
**Access:** `ACCESSIBLE`  
**URL:**  
https://www.icar-crida.res.in/CP-2012/statewiseplans/Maharastra(Pdf)/MAU,%20Parbhani/Maharashtra%2030-Osmanabad-%2031-12-2011.pdf

### Important pinpoints

- PDF/printed page 10: approximately 2-week delay and beginning of 4-week delay table.
- PDF/printed page 12: approximately 6-week delay; medium/deep and shallow assured-rainfall situations.
- PDF/printed page 14: approximately 8-week delay; crop substitutions including Tur → Bajra+Tur, Black Gram alternatives, Soybean → Kharif fallow + Rabi, and shallow-soil Bajra retention.
- PDF/printed page 21: terminal drought / early monsoon withdrawal management.

### Claims used

Detailed source for:

- 2/4/6/8-week delayed onset,
- soil/rainfall situation differences,
- Bhoom/Paranda lower-rainfall logic,
- crop/cropping-system substitutions,
- Rabi/fallow alternatives,
- protective irrigation and moisture-conservation measures,
- terminal drought and unusual rainfall management.

### Used by

Most detailed A3/A4 rules.

### Critical limitations

- This is a legacy plan.
- Legacy variety names must not be surfaced as current recommendations.
- Modern VNMKV/ICAR evidence must soften or override it when direct conflicts exist.
- A newer publicly accessible detailed Dharashiv 2/4/6/8-week table has not yet been located.

### Review status

`VERIFIED_WITH_LIMITATION`

---

## SRC-007 — VNMKV AICRP Dryland Agriculture Recommendation

**Institution:** VNMKV / AICRP for Dryland Agriculture  
**Recommendation date:** June 2024  
**Geography:** Marathwada  
**Source type:** Recent regional dryland recommendation  
**Evidence scope:** `DIRECT_CURRENT_REGIONAL`  
**Access:** `ACCESSIBLE`  
**URL:**  
https://www.vnmkv.ac.in/Content/Home/pdf/research/Dryland_Recommendation_All_24.07.2024.pdf

### Pinpoint

PDF page 6, recommendation 18 (June 2024).

### Claims used

If monsoon is delayed about 15 days:

- Green Gram, Pearl Millet, Cotton, Soybean, Maize, Sorghum and Pigeonpea may be sown up to first fortnight July.
- Reported research yield reductions:
  - Green Gram 22.51%
  - Pearl Millet 7.45%
  - other listed crops 15–17%

If monsoon is delayed about one month:

- Cotton, Soybean, Sorghum and Pigeonpea may be sown through the second fortnight of July,
- with about 40% reported yield reduction under the studied dryland condition.

### Used by

- A3 delayed windows
- A4 conflict handling for late Soybean
- corroboration of delayed Tur/Bajra

### Limitations

- Marathwada regional, not field-specific.
- Research yield reductions must not be presented as farmer-specific predictions.
- The 15-day crop list names **Green Gram, not Black Gram**.

### Review status

`VERIFIED_WITH_LIMITATION`

---

## SRC-008 — VNMKV Soil and Water Conservation Engineering Practical Manual

**Institution:** VNMKV  
**Source type:** University technical manual  
**Evidence scope:** `CONTEXT_ONLY`  
**Access:** `ACCESSIBLE`  
**URL:**  
https://coap.vnmkv.ac.in/Content/Home/assets/pdf/DepAgriEngineer/Practical-manual-ENGG-121.pdf

### Pinpoint

PDF page 45, bund-design table:

- Shallow: 7.5–22.5 cm
- Medium: 22.5–45 cm
- Medium-deep: 45–90 cm

### Used by

A2 soil-depth modelling context.

### Critical limitation

This is a soil/water-conservation engineering table, not a Dharashiv crop-suitability classification.

It does **not** directly validate Pik Nirnay’s provisional `<50 / 50–100 / >100 cm` thresholds.

### Review status

`VERIFIED_WITH_LIMITATION`

---

## SRC-009 — PoCRA GIS Soil Services

**Institution:** PoCRA / Government of Maharashtra  
**Source type:** Geospatial soil-data service  
**Evidence scope:** `CONTEXT_ONLY`  
**Access:** `ACCESSIBLE`  
**URL:**  
https://gis.mahapocra.gov.in/html/soil-services/nbss-soil-advisory.html

### Claims used

Village/location-level layers can include soil depth, water-holding capacity, texture and organic carbon.

### Used by

Future soil-assistance design only.

### Limitation

Map data must not be treated as exact field measurement.

### Review status

`VERIFIED_WITH_LIMITATION`

---

## SRC-010 — Maharashtra Agricultural Contingency Preparedness 2022

**Institution:** ICAR / ICAR-CRIDA  
**Date:** 2022  
**Geography:** Maharashtra  
**Evidence scope:** `CORROBORATING_CURRENT` relative to legacy district plan  
**Access:** `ACCESSIBLE`  
**URL:**  
https://www.icar.gov.in/hi/node/15919

### Claims used

- Suggested Soybean cultivation up to approximately 25 July in the delayed-monsoon situation.
- Called for experiments quantifying yield decline with each week of delayed sowing.

### Used by

A3/A4 late-Soybean conflict handling.

### Limitation

State-level contingency meeting, not Dharashiv deterministic field guidance.

### Review status

`VERIFIED_WITH_LIMITATION`

---

## SRC-011 — Maharashtra Agricultural Contingency Preparedness 2023

**Institution:** ICAR / ICAR-CRIDA  
**Date:** 2023  
**Geography:** Maharashtra  
**Evidence scope:** `CORROBORATING_CURRENT` relative to legacy district plan  
**Access:** `ACCESSIBLE`  
**URL:**  
https://www.icar.gov.in/hi/virtual-interface-meeting-enhancing-preparedness-agricultural-contingencies-kharif-2023-maharashtra

### Claims used

- Experts concluded Soybean could be sown through July-end in the contingency context.
- Intercropping was suggested when Soybean sowing occurs after 15 July.

### Used by

A3/A4 late-Soybean conflict handling.

### Limitation

State-level expert discussion, not a district-specific rule.

### Review status

`VERIFIED_WITH_LIMITATION`

---

## SRC-012 — VNMKV late-sown Pearl Millet recommendation

**Institution:** VNMKV, Agronomy  
**Recommendation year:** 2019  
**Geography:** Marathwada  
**Source type:** Historical regional research recommendation  
**Evidence scope:** `DIRECT_HISTORICAL_REGIONAL`  
**Access:** `UNSTABLE`

### Indexed claim

For late-sown Pearl Millet in Marathwada, sowing around **25 July ± 5 days** with a specified management package was recommended.

The recommendation is explicitly listed under **2019** VNMKV research recommendations.

### Source locations

Search-indexed VNMKV Agronomy research material and VNMKV accreditation material have contained this recommendation, but direct deep links were unstable during the 2026-09-27 review.

### Used by

- A3 late-July Bajra
- A4 corroboration of late-July Bajra

### Critical correction from V0.1

This must **not** be classified as current evidence.

It is historical regional research that remains useful as corroboration.

### Review status

`UNSTABLE_SOURCE`

---

## SRC-013 — VNMKV Decadal Research Achievements in Dryland Farming

**Institution:** VNMKV  
**Geography:** Marathwada  
**Source type:** Regional dryland research compilation  
**Evidence scope:** `CORROBORATING_CURRENT` / historical compilation  
**Access:** `ACCESSIBLE` when source link resolves  
**URL:**  
https://www.vnmkv.ac.in/Content/Home/pdf/research/Decadal_Research_Achivements_in_dryland_farming.pdf

### Claims used

Regional contingency work includes systems such as:

- Soybean + Pigeonpea
- Pearl Millet + Pigeonpea
- exceptional late-sowing systems into early August

### Used by

A3/A4 exceptional intercropping scenarios.

### Limitation

Regional evidence may be more permissive than Dharashiv legacy district guidance.

### Review status

`VERIFIED_WITH_LIMITATION`

---

## SRC-014 — ICAR-CRIDA Maharashtra Kharif 2024 contingency meeting

**Institution:** ICAR-CRIDA / Maharashtra Department of Agriculture  
**Date:** 5 June 2024  
**Geography:** Maharashtra  
**Evidence scope:** `CORROBORATING_CURRENT`  
**Access:** `ACCESSIBLE`  
**URL:**  
https://www.icar-crida.res.in/kharif-2024-for-Maharashtra.html

### Claims used

- BBF was advised in major crops, especially Pigeonpea, to drain excess rainwater.
- Alternative crops/varieties were discussed.

### Used by

A4 heavy-rain/waterlogging advisory corroboration.

### Limitation

No detailed Dharashiv crop-transition table is provided.

### Review status

`VERIFIED`

---

## SRC-015 — ICAR-CRIDA Maharashtra Kharif 2025 contingency meeting

**Institution:** ICAR-CRIDA / Maharashtra Department of Agriculture  
**Date:** 14 May 2025  
**Geography:** Maharashtra  
**Evidence scope:** `CORROBORATING_CURRENT`  
**Access:** `ACCESSIBLE`  
**URL:**  
https://icar-crida.res.in/Interface-meeting.html

### Claims used

- BBF/drainage advice under excess-rain conditions.
- Short-term rainfall forecast and waterlogging advice were emphasized.
- Rainfall conservation for supplemental irrigation / Rabi area was discussed.

### Used by

A4 climate-scenario advisory corroboration.

### Limitation

No detailed Dharashiv 2/4/6/8-week crop-transition table.

### Review status

`VERIFIED`

---

# 5. Rule-to-source map

## 5.1 Two-week delayed onset

| Rule | Sources | Evidence status |
|---|---|---|
| `R-DHAR-ONSET-2W-SOY` | SRC-006 + SRC-007 | Corroborated |
| `R-DHAR-ONSET-2W-PP` | SRC-006 + SRC-007 | Corroborated |
| `R-DHAR-ONSET-2W-PM` | SRC-006 + SRC-007 | Corroborated where farming situation applies |
| `R-DHAR-ONSET-2W-BG` | SRC-006 only | Legacy district rule |

## 5.2 Four-week delayed onset

| Rule | Sources | Evidence status |
|---|---|---|
| `R-DHAR-ONSET-4W-PP` | SRC-006 + SRC-007 | Corroborated |
| `R-DHAR-ONSET-4W-BG` | SRC-006 | Legacy district rule |
| `R-DHAR-ONSET-4W-SOY` | SRC-006 + SRC-007 + SRC-010 + SRC-011 | Conflicting evidence → compare alternative, do not auto-remove Soybean |
| `R-DHAR-ONSET-4W-PM` | SRC-006 | Legacy district rule |

## 5.3 Six-week delayed onset

| Rule | Sources | Evidence status |
|---|---|---|
| `R-DHAR-ONSET-6W-PP-MD` | SRC-006 | Legacy district |
| `R-DHAR-ONSET-6W-PP-SH` | SRC-006 | Legacy district |
| `R-DHAR-ONSET-6W-PP-LOWRF-MD` | SRC-006 | Multiple alternatives → review required |
| `R-DHAR-ONSET-6W-BG-MD-ASSURED` | SRC-006 | Legacy district |
| `R-DHAR-ONSET-6W-BG-SH-ASSURED` | SRC-006 | Product mapping needed because source alternatives fall outside V1 |
| `R-DHAR-ONSET-6W-BG-MD-LOWRF` | SRC-006 | Legacy district |
| `R-DHAR-ONSET-6W-BG-SH-LOWRF` | SRC-006 | Product mapping needed |
| `R-DHAR-ONSET-6W-SOY` | SRC-006 + SRC-007 + SRC-010 + SRC-011 | Conflicting evidence → strong comparison with Soybean+Tur |
| `R-DHAR-ONSET-6W-PM` | SRC-006 + SRC-012 | Legacy district + historical regional corroboration |

## 5.4 Eight-week delayed onset

| Rule | Sources | Evidence status |
|---|---|---|
| `R-DHAR-ONSET-8W-PP` | SRC-006 + SRC-013 | Legacy district + regional corroboration |
| `R-DHAR-ONSET-8W-BG` | SRC-006 | Source alternatives must be preserved |
| `R-DHAR-ONSET-8W-SOY` | SRC-006 | Explicit legacy district Rabi/fallow transition |
| `R-DHAR-ONSET-8W-PM` | SRC-006 | Legacy district only |
| `R-DHAR-ONSET-8W-SP` | SRC-006 + SRC-013 | Conflicting → review required |

---

# 6. Scenario-advisory evidence map

These are not candidate-ranking rules.

| Scenario | Sources | Permitted V1 use | Prohibited V1 use |
|---|---|---|---|
| Prolonged dry spell | SRC-006 + contextual SRC-002 | warning + source-backed mitigation | automatic crop ranking or failure probability |
| Early monsoon withdrawal | SRC-006 | terminal-drought warning / Rabi context | numeric failure probability |
| Heavy rain / waterlogging | SRC-006 + SRC-014 + SRC-015 | drainage/BBF warning | inferring drainage from soil depth |

---

# 7. Product-derived decisions

## P-DERIVED-001 — Soil category model

Accepted categorical enum:

```text
SHALLOW
MEDIUM_DEEP
DEEP
UNKNOWN
```

Evidence basis:

- SRC-002
- SRC-003
- SRC-006
- SRC-008

### Numeric thresholds

The earlier prototype thresholds:

```text
SHALLOW       < 50 cm
MEDIUM_DEEP   50–100 cm
DEEP          > 100 cm
```

are **not yet evidence-frozen**.

They may be retained in UX notes as provisional cues, but Claude must not hard-code them into agronomic rules until separately approved.

**Status:** `REVIEW_REQUIRED` for numeric cut-offs; categorical model accepted.

---

## P-DERIVED-002 — Supported set vs displayed options

Pik Nirnay may support six crop/system profiles while displaying only 3–4 contextually relevant candidates.

**Status:** Approved product decision.

---

## P-DERIVED-003 — No supported V1 Kharif replacement

When the source lists only non-V1 crops (e.g. fodder Sorghum, fodder Maize, Niger) plus Rabi/fallow options, Pik Nirnay may use:

```text
NO_SUPPORTED_KHARIF_OPTION
```

but must retain all original source alternatives in provenance.

**Status:** Approved prototype interpretation.

---

## P-DERIVED-004 — Conflict-aware rule

Where recent regional/state and legacy district sources disagree:

```text
REVIEW_REQUIRED
```

or:

```text
COMPARE_ALTERNATIVE
```

must be preferred to false certainty.

**Status:** Approved core principle.

---

# 8. Evidence gaps after review

## GAP-001 — Updated detailed Dharashiv contingency table

No newer publicly accessible Dharashiv-specific detailed 2/4/6/8-week table was found during the review.

**Impact:** detailed A4 crop transitions remain prototype rules tagged as legacy district evidence.

---

## GAP-002 — Soil numeric cut-offs

The categorical soil model is supported, but the exact V1 `<50 / 50–100 / >100 cm` boundaries are product-derived and not sufficiently validated for agronomic rule execution.

**Impact:** do not hard-code them into crop-selection logic yet.

---

## GAP-003 — Effective sowing-moisture / monsoon-onset algorithm

No approved cross-crop V1 algorithm yet defines:

```text
SOWING_MOISTURE_READY
```

**Impact:** calendar date alone cannot authorize sowing.

---

## GAP-004 — Dry-spell detector

The legacy district threshold wording is ambiguous.

**Impact:** use semantic `PROLONGED_DRY_SPELL` until Phase B + current agronomic evidence define a defensible detector.

---

## GAP-005 — Drainage condition

Soil depth is not equivalent to drainage.

**Impact:** waterlogging advice cannot rank a field solely from `SHALLOW/MEDIUM_DEEP/DEEP`.

---

## GAP-006 — Current variety list

Legacy variety names must not be copied directly from SRC-006.

**Impact:** use abstract requirements such as `EARLY_OR_SHORT_DURATION_REQUIRED`.

---

## GAP-007 — Comparative climate-risk scoring

Evidence supports candidate changes and warnings, but not yet a calibrated universal numeric risk score.

**Impact:** no arbitrary weighted score before a separate reviewed scoring design.

---

## GAP-008 — Late-sown Pearl Millet source freshness

The 25 July ± 5 days recommendation is from 2019 regional research and its direct deep-link source is unstable.

**Impact:** retain as historical corroboration, not as sole evidence for current farmer advice.

---

# 9. Mandatory review protocol

Before a research/design node is frozen:

1. **Re-open primary sources.**
2. **Search for newer sources.**
3. **Actively seek contradictions.**
4. **Test missing crops, soil contexts, date boundaries, locations and UNKNOWN values.**
5. **Check interpretation strength:** “consider” must not become “best”; research yield loss must not become individual prediction.
6. **Check software abstraction:** avoid collapsing distinct concepts or forcing decisions where sources provide alternatives.
7. **Separate evidence from product assumptions.**
8. **Identify downstream documents affected by revisions.**
9. Use only these review outcomes:

```text
READY_TO_FREEZE
READY_WITH_LIMITATION
REVIEW_REQUIRED
DEFERRED
```

---

# 10. Evidence-ready rule definition

A rule is ready for Claude only when:

- it has a stable rule ID,
- canonical source IDs are recorded,
- relevant pinpoint location is available,
- source age/scope is explicit,
- conflicts are represented,
- product-derived transformations are labelled,
- required domain inputs exist,
- and the review state permits implementation.

---

# 11. Freeze decision

| Workstream | Review result |
|---|---|
| A1 Crop shortlist | `READY_TO_FREEZE` |
| A2 Soil category model | `READY_WITH_LIMITATION` — categories yes; numeric cut-offs not frozen |
| A3 Sowing-window model | `READY_TO_FREEZE` |
| A4 Contingency rule model | `READY_WITH_LIMITATION` — legacy district rules explicitly tagged |
| Evidence Register | `READY_WITH_LIMITATION` |
| C1/C2/C3 implementation | May proceed if Claude does not hard-code unresolved soil cut-offs or unresolved weather thresholds |
| Phase B | Not started |

## Overall decision

The evidence set is sufficiently structured to proceed to **C1/C2/C3 domain-model implementation**.

The unresolved gaps are now explicit and can be represented in the domain model without pretending they are solved.
