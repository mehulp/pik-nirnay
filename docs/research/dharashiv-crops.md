# Dharashiv V1 Crop and Cropping-System Shortlist

**Project:** Pik Nirnay / पीक निर्णय  
**Workstream:** A1 — Dharashiv Crop Shortlist  
**Version:** Revised after source re-audit  
**Status:** Proposed V1 baseline  
**Scope:** Rain-fed / limited-irrigation Kharif decision support in Dharashiv district

---

## 1. Purpose

Define the crop and cropping-system options that Pik Nirnay V1 is allowed to model.

The shortlist must balance three things:

1. **Current farmer relevance** — crops that are actually important in present-day Dharashiv.
2. **Climate-decision usefulness** — options that behave differently under delayed monsoon, shallow soil and dry spells.
3. **Prototype discipline** — enough variation to exercise the decision engine without attempting to model every crop grown in the district.

The application may support more crop profiles than it displays at one time. V1 should normally compare only **3–4 relevant options** for a given field/context.

---

## 2. Major change from A1 v1

The first A1 draft proposed five options:

- Soybean
- Pigeonpea
- Soybean + Pigeonpea
- Pearl Millet
- Pearl Millet + Pigeonpea

After re-auditing current district crop statistics, this is incomplete.

**Black gram / Udid must be added.**

Maharashtra's Final Advance Estimates for 2024–25 report approximately:

| Kharif crop | Dharashiv area |
|---|---:|
| Soybean | 463,726 ha |
| Black gram / Udid | 51,342 ha |
| Pigeonpea / Tur | 43,359 ha |
| Green gram / Mung | 11,083 ha |
| Maize | 8,722 ha |
| Pearl Millet / Bajra | 1,257 ha |
| Kharif Sorghum / Jowar | 1,069 ha |

(Official source reports area in "00" ha; figures above are converted to hectares.)

This strongly supports including Udid in a present-day Dharashiv prototype.

---

## 3. Proposed V1 supported set

V1 should support **six** crop/cropping-system profiles, while normally returning no more than 3–4 decision cards for an individual scenario.

### Core current crops

1. Soybean / सोयाबीन
2. Black gram / Udid / उडीद
3. Pigeonpea / Tur / तूर

### Diversification / climate-contingency systems

4. Soybean + Pigeonpea / सोयाबीन + तूर
5. Pearl Millet / Bajra / बाजरी
6. Pearl Millet + Pigeonpea / बाजरी + तूर

This is deliberately a support set, not a claim that all six should appear for every farmer.

---

# 4. Option profiles

## 4.1 Soybean / सोयाबीन

**Include:** Yes — mandatory core crop.

### Why it belongs

- Maharashtra 2024–25 district estimates show soybean at about **4.64 lakh ha in Dharashiv**, overwhelmingly larger than the other Kharif crops in the district.
- A 2024 PoCRA monitoring study in selected Dharashiv/Latur villages similarly describes soybean as the major Kharif crop, around 80% of cultivated area in the studied locations.
- VNMKV's Dharashiv college lists soybean among the district's main crops.
- Dharashiv contingency plans explicitly change soybean strategy as monsoon delay becomes more severe.

### Climate-decision role

Soybean is the **baseline choice** against which alternatives are compared.

It is useful because:

- current farmer familiarity is high,
- large area means market/input availability is likely to be relevant,
- dry spells during critical growth stages can materially affect the crop,
- late-sowing guidance progressively shifts from sole soybean toward intercropping or Rabi planning.

### V1 role

`CORE_BASELINE`

---

## 4.2 Black Gram / Udid / उडीद

**Include:** Yes — added after A1 re-audit.

### Why it belongs

Maharashtra's 2024–25 final district estimates report around **51,342 ha of Kharif Udid in Dharashiv**, slightly more area than Tur.

ICAR's 2025 Maharashtra Kharif advisory provides current black-gram guidance and improved varieties.

The Dharashiv contingency plan also explicitly includes black gram and shows an important climate pattern:

- short monsoon delay: black gram may continue,
- greater delay: the recommended crop/system changes,
- severe delay: fodder crops, alternative crops or preparation for Rabi may replace it.

### Why it is valuable to Pik Nirnay

Udid gives us a very different decision pattern from Bajra:

- it is currently important in the district,
- it may be a normal-season choice,
- but it becomes less attractive as sowing delay becomes severe.

That is exactly the kind of temporal trade-off the decision engine should expose.

### V1 role

`CORE_CURRENT_CROP`

---

## 4.3 Pigeonpea / Tur / तूर

**Include:** Yes — mandatory core crop.

### Why it belongs

- Maharashtra 2024–25 district estimates report approximately **43,359 ha** of Tur in Dharashiv.
- VNMKV's Dharashiv college lists red gram among the district's main crops.
- Current ICAR Maharashtra advisories explicitly cover pigeonpea varieties, sowing periods, intercropping and protective irrigation.
- The Dharashiv contingency plan retains or changes pigeonpea according to soil depth and monsoon delay.

### Climate-decision role

Tur adds:

- longer crop duration,
- stronger soil-depth interaction,
- protective-irrigation relevance,
- several intercropping possibilities,
- a different market/financial timeline from soybean and Udid.

### V1 role

`CORE_CURRENT_CROP`

---

## 4.4 Soybean + Pigeonpea / सोयाबीन + तूर

**Include:** Yes — mandatory cropping-system option.

### Why it belongs

This is not merely a theoretical combination.

- Current ICAR Maharashtra guidance recommends pigeonpea + soybean intercropping.
- The Dharashiv contingency plan specifically changes sole soybean toward soybean + pigeonpea when monsoon delay becomes substantial.
- It therefore represents a real alternative to "keep sowing sole soybean late."

### Climate-decision role

This option lets Pik Nirnay model **diversification**, rather than pretending crop selection always means choosing one monocrop.

### Important future requirements

A4/Agronomy work must eventually represent:

- row ratio,
- suitable variety duration,
- sowing-window conditions.

Do not treat the intercrop as simply the sum of two independent crop profiles.

### V1 role

`DIVERSIFICATION_SYSTEM`

---

## 4.5 Pearl Millet / Bajra / बाजरी

**Include:** Yes — but classify correctly.

### Current district importance

Maharashtra 2024–25 estimates report only around **1,257 ha of Bajra in Dharashiv**.

Therefore Pik Nirnay must **not describe Bajra as a dominant current Dharashiv crop**.

### Why retain it anyway

Bajra is included because of its **contingency value**, not current acreage.

- The Dharashiv contingency plan retains pearl millet in shallow-soil / delayed-monsoon scenarios where other crop choices change.
- VNMKV regional research has a specific late-sown pearl-millet recommendation around late July.
- VNMKV's 2024 dryland delayed-monsoon recommendation includes pearl millet among crops that can remain viable under an approximately 15-day monsoon delay.

### Product consequence

Bajra should generally surface when its **climate-contingency characteristics make it relevant**.

It should not automatically appear in every normal-June comparison just because it is supported by the engine.

### V1 role

`CLIMATE_CONTINGENCY_CROP`

---

## 4.6 Pearl Millet + Pigeonpea / बाजरी + तूर

**Include:** Yes — mandatory severe-delay contingency system.

### Why it belongs

This is one of the strongest repeated crop-system transitions in the Dharashiv contingency plan.

As monsoon delay becomes more severe, several sole crops transition toward pearl millet + pigeonpea, especially in shallow-soil situations.

At approximately eight weeks of delayed onset, the district plan explicitly shifts pigeonpea and sorghum situations toward pearl millet + pigeonpea with an early-maturing pigeonpea requirement.

### Product consequence

This option should primarily surface in **late / severe-delay scenarios**, not as a universal default.

### V1 role

`SEVERE_DELAY_CONTINGENCY_SYSTEM`

---

# 5. Why the supported set is six rather than five

The first prototype should still show only **3–4 relevant risk cards**.

Supporting six domain profiles does not mean displaying six choices.

Example:

### Normal late-June scenario

Potential candidates might include:

```text
Soybean
Udid
Tur
Soybean + Tur
```

### Severe late-July / shallow-soil scenario

Potential candidates might instead include:

```text
Soybean + Tur
Bajra
Bajra + Tur
Tur (only if conditions support it)
```

This makes the product context-sensitive without expanding into a generic crop catalogue.

---

# 6. Crops deliberately deferred

## 6.1 Kharif Sorghum / Jowar

**Decision:** Defer.

This conclusion is now stronger than in A1 v1.

The 2024–25 Maharashtra district estimates show only about **1,069 ha of Kharif Jowar in Dharashiv**, while the same official dataset reports a very large **Rabi Jowar area (roughly 1.73 lakh ha)**.

So Jowar is highly relevant to Dharashiv agriculture, but its stronger present-day role is Rabi rather than the Kharif first-sowing decision Pik Nirnay V1 is targeting.

The Kharif contingency plan also frequently changes sole sorghum toward other systems as delayed onset becomes severe.

**Future:** strong candidate for a later Rabi module.

---

## 6.2 Green Gram / Mung

**Decision:** Defer.

Current 2024–25 Dharashiv area is approximately **11,083 ha**, so it is not irrelevant.

VNMKV's 2024 delayed-monsoon research also includes green gram under a roughly 15-day delay.

However:

- current district Udid area is substantially larger,
- both are short-duration pulses,
- adding both now creates overlapping rule work.

Udid is therefore the stronger V1 representative of this decision space.

---

## 6.3 Maize

**Decision:** Defer.

Current 2024–25 Dharashiv area is roughly **8,722 ha**.

Maize appears in contingency alternatives, but is not required to validate the first crop-risk engine.

---

## 6.4 Cotton

**Decision:** Exclude from V1.

The 2024–25 district estimate shows very small cotton area in Dharashiv compared with soybean/pulses.

Cotton would also introduce:

- substantially different duration,
- input-cost structure,
- pest-management risk,
- market risk.

It adds disproportionate complexity for the first prototype.

---

## 6.5 Sunflower / Sesame / Niger / Castor

**Decision:** Defer.

Several appear in older contingency plans, especially under severe delays.

They are useful future alternatives but not necessary for V1.

---

## 6.6 Sugarcane / grapes / irrigated horticulture

**Decision:** Out of V1.

These do not match the initial rain-fed / limited-irrigation Kharif persona.

---

## 6.7 Chickpea / Rabi Sorghum / Wheat

**Decision:** Out of current V1, but strategically important.

These are Rabi crops.

However, A3/A4 may legitimately produce an outcome such as:

```text
DO_NOT_FORCE_KHARIF_CROP
PREPARE_FOR_RABI
```

A future Rabi module could then compare chickpea, Rabi jowar and other suitable crops.

---

# 7. V1 crop IDs

Recommended domain identifiers:

```text
SOYBEAN
BLACK_GRAM
PIGEONPEA
SOYBEAN_PIGEONPEA
PEARL_MILLET
PEARL_MILLET_PIGEONPEA
```

Farmer-facing names:

| ID | English | Marathi | Classification |
|---|---|---|---|
| `SOYBEAN` | Soybean | सोयाबीन | Core baseline |
| `BLACK_GRAM` | Black gram / Udid | उडीद | Core current crop |
| `PIGEONPEA` | Pigeonpea / Tur | तूर | Core current crop |
| `SOYBEAN_PIGEONPEA` | Soybean + Pigeonpea | सोयाबीन + तूर | Diversification system |
| `PEARL_MILLET` | Pearl Millet / Bajra | बाजरी | Climate-contingency crop |
| `PEARL_MILLET_PIGEONPEA` | Pearl Millet + Pigeonpea | बाजरी + तूर | Severe-delay contingency system |

---

# 8. Candidate-selection principle

The decision engine must distinguish:

```text
SUPPORTED_BY_V1
```

from:

```text
RELEVANT_FOR_THIS_SCENARIO
```

A supported crop should not automatically appear on the result screen.

Candidate generation should eventually use:

```text
location
+
soil depth
+
sowing timing
+
climate / monsoon context
+
irrigation availability
```

to reduce the supported set to approximately **3–4 meaningful options** before risk comparison.

---

# 9. Evidence and provenance

## E-A1-01 — Maharashtra Final Advance Estimates 2024–25

**Source:** Department of Agriculture, Maharashtra  
**Use:** Current district-level crop area, production and productivity.

For Dharashiv, the official estimates support approximately:

- Soybean: 463,726 ha
- Udid: 51,342 ha
- Tur: 43,359 ha
- Mung: 11,083 ha
- Maize: 8,722 ha
- Bajra: 1,257 ha
- Kharif Jowar: 1,069 ha

They also show that Rabi Jowar has a far larger district area than Kharif Jowar.

Source:  
https://krishi.maharashtra.gov.in/Site/Upload/GR/DISTRICTWISE%20APY-2024-25.pdf

## E-A1-02 — PoCRA Concurrent Monitoring Round X, 2024

The selected Dharashiv/Latur field study reports:

- extensive shallow-soil conditions,
- farmers growing shallow-rooted crops such as sorghum, soybean and moong in shallow soil,
- soybean as a major Kharif crop in the visited context, around 80% of cultivated area,
- severe crop stress during the long 2023 dry spell.

Source:  
https://mahapocra.gov.in/assets/docs/mne/Final_Report_SambodhiCM_PoCRA_1June2024.pdf

## E-A1-03 — VNMKV College of Agriculture, Dharashiv

Lists soybean and red gram among Dharashiv's main crops.

Source:  
https://coaob.vnmkv.ac.in/page.php?slug=about_us

## E-A1-04 — ICAR Kharif Agro-Advisories 2025, Maharashtra

Provides current Maharashtra guidance for:

- soybean,
- pigeonpea,
- black gram,
- intercropping pigeonpea with soybean, bajra, sorghum, moong and urad.

Source:  
https://icar.gov.in/sites/default/files/Circulars/ICAR%20En-Kharif%20Agro-Advisories%20for%20Farmers%202025.pdf

## E-A1-05 — Dharashiv/Osmanabad District Agriculture Contingency Plan

Provides district-specific delayed-onset crop-system transitions, including:

- soybean → soybean+pigeonpea,
- pigeonpea / sorghum → pearl millet+pigeonpea under severe delay,
- black gram → alternate crop/system as delay increases,
- soybean → Kharif fallow followed by Rabi under approximately eight-week delay.

Source:  
https://www.icar-crida.res.in/cp-2012/statewiseplans/Maharastra(Pdf)/MAU,%20Parbhani/Maharashtra%2030-Osmanabad-%2031-12-2011.pdf

## E-A1-06 — VNMKV AICRP Dryland Agriculture, 2024

Regional delayed-monsoon research includes green gram, pearl millet, soybean, maize, sorghum and pigeonpea under delayed onset, with the eligible set narrowing and yield penalty increasing with greater delay.

Source:  
https://www.vnmkv.ac.in/Content/Home/pdf/research/Dryland_Recommendation_All_24.07.2024.pdf

---

# 10. A1 implications for existing project documents

Because Black Gram/Udid is now included:

### A3 must be revised

`dharashiv-sowing-windows.md` currently models five crop/cropping systems.

It must add:

```text
BLACK_GRAM
```

with its current / delayed / contingency timing behaviour.

### A4 must include Black Gram

Black gram is especially useful for A4 because its recommendation changes substantially as monsoon delay increases.

### PRD wording

The PRD should say:

> V1 supports a small curated Dharashiv crop/cropping-system set and normally displays 3–4 contextually relevant alternatives.

It should not imply that the supported set itself is limited to exactly 3–4 crops.

---

# 11. A1 exit decision

**Recommended V1 supported set:**

```text
SOYBEAN
BLACK_GRAM
PIGEONPEA
SOYBEAN_PIGEONPEA
PEARL_MILLET
PEARL_MILLET_PIGEONPEA
```

This set is stronger than A1 v1 because it represents both:

- **what Dharashiv farmers are actually growing now**, and
- **the contingency alternatives that become relevant when the monsoon behaves badly**.

**Proposed status: READY TO FREEZE after product-owner approval.**
