# Dharashiv V1 Sowing Window Model

**Project:** Pik Nirnay / पीक निर्णय  
**Workstream:** A3 — Sowing Window Matrix  
**Version:** V3 — revised after A1 crop re-audit  
**Status:** Ready to freeze for V1  
**Scope:** First sowing decision for rain-fed / limited-irrigation Kharif farming in Dharashiv district  
**Depends on:** A1 Crop Shortlist, A2 Soil Depth Model

---

## 1. Purpose

Define how Pik Nirnay V1 should interpret sowing timing for the six supported crop/cropping-system profiles:

- Soybean
- Black gram / Udid
- Pigeonpea / Tur
- Soybean + Pigeonpea
- Pearl Millet / Bajra
- Pearl Millet + Pigeonpea

A3 does not assign final crop risk. It defines the timing context that A4 and the decision engine will use.

---

## 2. Scope boundary: first sowing only

A3 applies before the crop is established.

It does not cover:

- re-sowing after poor germination,
- re-sowing after seedling mortality,
- crop replacement after flood/dry-spell damage,
- mid-season salvage.

Those require separate contingency rules.

---

## 3. Timing is two-dimensional

Pik Nirnay must retain both:

```text
exact_sowing_date
+
monsoon_delay_context
```

The same calendar date can mean different things depending on whether effective monsoon rainfall arrived normally or late.

`monsoon_delay_days` may be unknown. The application must not manufacture it from date alone.

---

## 4. Internal status

```text
SowingWindowStatus
    NORMAL_WINDOW
    DELAYED_WINDOW
    CONTINGENCY_WINDOW
    CONDITIONAL_REVIEW
    OUTSIDE_V1_WINDOW
```

| Status | Meaning |
|---|---|
| `NORMAL_WINDOW` | Normal sowing period, subject to adequate establishment moisture |
| `DELAYED_WINDOW` | Still supported, but delay-related downside must be shown |
| `CONTINGENCY_WINDOW` | Abnormal/late sowing option supported only as a contingency |
| `CONDITIONAL_REVIEW` | Outcome depends strongly on soil, rainfall zone, variety or monsoon-delay context |
| `OUTSIDE_V1_WINDOW` | V1 should not offer this as a normal fresh-sowing option |

---

## 5. Calendar bands

```text
BEFORE_15_JUNE     = before 15 Jun
SECOND_HALF_JUNE   = 15–30 Jun
FIRST_HALF_JULY    = 01–15 Jul
LATE_JULY_A        = 16–20 Jul
LATE_JULY_B        = 21–31 Jul
FIRST_HALF_AUGUST  = 01–15 Aug
AFTER_15_AUGUST    = after 15 Aug
```

Exact date must always be retained.

---

# 6. Crop-by-crop timing model

## 6.1 Soybean / सोयाबीन

| Period | Status | Interpretation |
|---|---|---|
| Before 15 Jun | `CONDITIONAL_REVIEW` | Main rain-fed persona should wait for effective establishment moisture |
| 15–30 Jun | `NORMAL_WINDOW` | Strong normal window |
| 1–15 Jul | `NORMAL_WINDOW` / `DELAYED_WINDOW` | Current Maharashtra advice targets completion around mid-July; monsoon context matters |
| 16–20 Jul | `DELAYED_WINDOW` | Late; downside must be shown |
| 21–25 Jul | `CONTINGENCY_WINDOW` | Exceptional delayed-monsoon option only |
| 26–31 Jul | `CONDITIONAL_REVIEW` | Some Maharashtra contingency evidence permits month-end, but not as routine sowing |
| 1–15 Aug | `OUTSIDE_V1_WINDOW` | Dharashiv severe-delay plan moves soybean toward Kharif fallow/Rabi planning |
| After 15 Aug | `OUTSIDE_V1_WINDOW` | Outside V1 |

Do not treat late-July soybean as equivalent to normal June soybean.

---

## 6.2 Black Gram / Udid / उडीद

Black gram is the main A3 addition after A1 V2.

The old Dharashiv district profile gives a broad rain-fed window of roughly 15 June–30 July, but the same district contingency plan changes away from black gram much earlier when the monsoon itself is delayed.

That makes black gram a strong example of why `calendar_date` and `monsoon_delay_context` must remain separate.

| Period | Status | Interpretation |
|---|---|---|
| Before 15 Jun | `CONDITIONAL_REVIEW` | Wait for adequate rain/moisture; V1 has no crop-specific pre-15-Jun rule |
| 15–30 Jun | `NORMAL_WINDOW` | Normal district window |
| 1–15 Jul | `CONDITIONAL_REVIEW` | Calendar is still within the legacy district window, but at ~4-week delayed onset the district plan changes black gram to soybean+pigeonpea |
| 16–31 Jul | `CONDITIONAL_REVIEW` | Under ~6-week delay, black gram is replaced by other systems or Rabi planning depending on soil/rainfall situation |
| 1–15 Aug | `OUTSIDE_V1_WINDOW` | At ~8-week delay the district plan changes black gram to Niger/fodder/fallow for Rabi |
| After 15 Aug | `OUTSIDE_V1_WINDOW` | Outside V1 |

### Product consequence

Do not expose one universal "last Udid sowing date."

A July black-gram decision must be evaluated using A4's monsoon-delay, soil and rainfall-zone rules.

---

## 6.3 Pigeonpea / Tur / तूर

Recent Maharashtra guidance distinguishes variety duration.

| Period | Status | Interpretation |
|---|---|---|
| 1–14 Jun | `CONDITIONAL_REVIEW` | Appropriate for suitable early varieties |
| 15–30 Jun | `NORMAL_WINDOW` | Strong normal window |
| 1–15 Jul | `NORMAL_WINDOW` / `DELAYED_WINDOW` | Supported for medium/late types; monsoon context matters |
| 16–31 Jul | `CONTINGENCY_WINDOW` / `CONDITIONAL_REVIEW` | Soil and rainfall zone become important |
| 1–15 Aug | `OUTSIDE_V1_WINDOW` as sole crop | Severe-delay guidance switches to pearl millet+pigeonpea |
| After 15 Aug | `OUTSIDE_V1_WINDOW` | Outside V1 |

Late-July Tur must not be implemented as one district-wide rule.

---

## 6.4 Soybean + Pigeonpea / सोयाबीन + तूर

| Period | Status | Interpretation |
|---|---|---|
| Before 15 Jun | `CONDITIONAL_REVIEW` | Effective rainfall and variety context required |
| 15–30 Jun | `NORMAL_WINDOW` | Supported diversification system |
| 1–15 Jul | `NORMAL_WINDOW` / `DELAYED_WINDOW` | Supported |
| 16–31 Jul | `CONTINGENCY_WINDOW` | Important late-July alternative to sole soybean in Dharashiv contingency guidance |
| 1–15 Aug | `CONDITIONAL_REVIEW` | Broader regional evidence is more permissive than Dharashiv's severe-delay soybean rule |
| After 15 Aug | `OUTSIDE_V1_WINDOW` | Outside V1 |

Late sowing may require suitable duration varieties and row configuration.

---

## 6.5 Pearl Millet / Bajra / बाजरी

| Period | Status | Interpretation |
|---|---|---|
| Before 15 Jun | `CONDITIONAL_REVIEW` | Effective rainfall required |
| 15–30 Jun | `NORMAL_WINDOW` | Normal Kharif option |
| 1–15 Jul | `DELAYED_WINDOW` | Supported under delayed monsoon |
| 16–31 Jul | `CONTINGENCY_WINDOW` | VNMKV has a dedicated late-sown pearl-millet recommendation around late July |
| 1–15 Aug | `CONDITIONAL_REVIEW` | Dharashiv retains sole pearl millet in some shallow-soil severe-delay situations, not universally |
| After 15 Aug | `OUTSIDE_V1_WINDOW` | Outside V1 |

Bajra is a climate-contingency crop in this project, not a dominant-current-acreage crop.

---

## 6.6 Pearl Millet + Pigeonpea / बाजरी + तूर

| Period | Status | Interpretation |
|---|---|---|
| Before 15 Jun | `CONDITIONAL_REVIEW` | Effective rainfall/variety context required |
| 15–30 Jun | `NORMAL_WINDOW` | Supported intercropping concept |
| 1–15 Jul | `DELAYED_WINDOW` | Supported |
| 16–31 Jul | `CONTINGENCY_WINDOW` | Major delayed-onset alternative |
| 1–15 Aug | `CONTINGENCY_WINDOW` with conditions | Strongest source-backed severe-delay system in the V1 shortlist; suitable early pigeonpea required |
| After 15 Aug | `OUTSIDE_V1_WINDOW` | Outside V1 |

---

# 7. Consolidated calendar-only matrix

This is not the final crop decision. A4 must modify it using monsoon delay, soil depth and rainfall zone.

| Crop / system | Before 15 Jun | 15–30 Jun | 1–15 Jul | 16–20 Jul | 21–31 Jul | 1–15 Aug | After 15 Aug |
|---|---|---|---|---|---|---|---|
| Soybean | Conditional | Normal | Normal / delayed | Delayed | Contingency → conditional near month-end | Outside | Outside |
| Black gram / Udid | Conditional | Normal | Conditional | Conditional | Conditional | Outside | Outside |
| Pigeonpea | Conditional for early varieties | Normal | Normal / delayed | Contingency | Conditional / soil-sensitive | Outside as sole crop | Outside |
| Soybean + Pigeonpea | Conditional | Normal | Normal / delayed | Contingency | Contingency | Conditional | Outside |
| Pearl Millet | Conditional | Normal | Delayed | Contingency | Contingency | Conditional | Outside |
| Pearl Millet + Pigeonpea | Conditional | Normal | Delayed | Contingency | Contingency | Contingency with conditions | Outside |

---

## 8. Rainfall-zone modifier

The Dharashiv contingency plan explicitly distinguishes lower-rainfall situations in Bhoom and Paranda.

A4 therefore needs:

```text
RainfallZone
    LOWER_RAINFALL_BHOOM_PARANDA
    OTHER_DHARASHIV
    UNKNOWN
```

This is a project abstraction from the district contingency plan, not a complete formal agro-climatic zoning system.

---

## 9. Variety-duration requirement

```text
VarietyRequirement
    ANY_APPROVED
    EARLY_OR_SHORT_DURATION_REQUIRED
    CROP_SPECIFIC_APPROVED_VARIETY_REQUIRED
    UNKNOWN
```

If a late-sowing option depends on shorter duration seed, the result card must say so.

Legacy variety names in old contingency plans must be revalidated before user-facing use.

---

## 10. Protective irrigation

Protective irrigation is a modifier, not an automatic calendar extension.

Never implement:

```text
if irrigation_available:
    extend_last_sowing_date()
```

A4 may use irrigation availability as a condition or risk-mitigation factor only where evidence supports it.

---

## 11. Establishment-moisture guard

```text
calendar_window != permission_to_sow
```

Before any usable sowing decision, a future rule must establish adequate sowing moisture/effective rainfall.

A3 does not invent one universal rainfall threshold for all six crop/system profiles.

---

## 12. Software contract

```text
SowingWindowAssessment
    crop_id
    proposed_sowing_date
    calendar_band
    status
    monsoon_delay_days?       # nullable
    variety_requirement
    conditions[]
    explanation_key
    source_ids[]
```

A3 returns an assessment, not a recommendation.

---

## 13. Evidence

### E-A3-01 — ICAR-CRIDA Dharashiv/Osmanabad contingency plan

District profile gives broad legacy windows and then changes crop/system choices at approximately 2-, 4-, 6- and 8-week delayed onset stages.

Source:  
https://www.icar-crida.res.in/CP-2012/statewiseplans/Maharastra(Pdf)/MAU,%20Parbhani/Maharashtra%2030-Osmanabad-%2031-12-2011.pdf

### E-A3-02 — VNMKV AICRP Dryland Agriculture, June 2024

For Marathwada, the recommendation distinguishes approximately 15-day and one-month monsoon delays and records substantial yield penalties with later sowing.

Source:  
https://www.vnmkv.ac.in/Content/Home/pdf/research/Dryland_Recommendation_All_24.07.2024.pdf

### E-A3-03 — ICAR Kharif Agro-Advisories 2025, Maharashtra

Current Maharashtra crop-specific advice includes:

- soybean completion around mid-July,
- pigeonpea sowing differentiated by variety duration,
- soybean+pigeonpea intercropping,
- current black-gram varieties.

Source:  
https://icar.gov.in/sites/default/files/Circulars/ICAR%20En-Kharif%20Agro-Advisories%20for%20Farmers%202025.pdf

### E-A3-04 — Maharashtra contingency preparedness discussions

ICAR Maharashtra meetings in 2022/2023 allowed later soybean in exceptional delayed-monsoon situations, while emphasizing yield decline and intercropping after mid-July.

Sources:  
https://icar.gov.in/hi/node/15919  
https://www.icar.gov.in/hi/virtual-interface-meeting-enhancing-preparedness-agricultural-contingencies-kharif-2023-maharashtra

### E-A3-05 — VNMKV late-sown pearl millet

VNMKV Agronomy reports a Marathwada late-sown pearl-millet recommendation centered around approximately 25 July ± 5 days.

Source:  
https://coap.vnmkv.ac.in/Content/Home/assets/pdf/Agronomy/Research.pdf

---

## 14. A3 exit decision

**Status: READY TO FREEZE FOR V1.**

The key rule is:

> Calendar timing narrows the candidate set, but A4 decides what the delayed-monsoon, soil and rainfall-zone context actually does to each crop/system.
