# Dharashiv V1 Climate Contingency Rule Matrix

**Project:** Pik Nirnay / पीक निर्णय  
**Workstream:** A4 — Climate Contingency Rules  
**Version:** V0.2 — revised after source re-audit  
**Status:** Proposed V1 baseline for prototype implementation  
**Scope:** Pre-sowing Kharif candidate selection plus climate-scenario advisory evidence for Dharashiv  
**Depends on:** A1 Crop Shortlist V2, A2 Soil Depth Model, A3 Sowing Window Model V3

---

## 1. Purpose

Translate Dharashiv/Marathwada agricultural contingency evidence into explicit, traceable software rules without overstating what the sources prove.

A4 now separates two different rule families:

```text
A. PRE_SOWING_CANDIDATE_RULE
   -> Can change which crop/cropping-system options are offered.

B. SCENARIO_ADVISORY
   -> Describes crop-management exposure/mitigation under a climate scenario.
   -> Must NOT automatically rank crops unless comparative evidence exists.
```

This distinction is essential.

---

## 2. Source-age warning

The publicly accessible Dharashiv/Osmanabad district contingency plan used for the detailed 2/4/6/8-week crop-change table is an older district document (2011-era plan).

ICAR-CRIDA states that many district contingency plans were subsequently updated nationally, but a newer public Dharashiv-specific detailed table could not be located during this review.

Therefore:

- detailed Dharashiv transition rules are acceptable for a **research prototype**,
- newer VNMKV/ICAR Maharashtra guidance must override or soften old rules where it conflicts,
- these rules must not be presented as field-validated current advice without later agronomist/KVK validation.

---

## 3. Evidence classes

Every rule should carry an evidence class:

```text
EvidenceClass
    CURRENT_REGIONAL
    LEGACY_DISTRICT_SPECIFIC
    CORROBORATED
    PRODUCT_DERIVED
    REVIEW_REQUIRED
```

Meaning:

| Class | Meaning |
|---|---|
| `CURRENT_REGIONAL` | Recent VNMKV/ICAR Maharashtra recommendation |
| `LEGACY_DISTRICT_SPECIFIC` | Explicit Dharashiv/Osmanabad contingency rule from the older district plan |
| `CORROBORATED` | Legacy district rule direction is supported by newer regional/state evidence |
| `PRODUCT_DERIVED` | Product interpretation of source alternatives because V1 has a smaller crop set |
| `REVIEW_REQUIRED` | Sources conflict or evidence is insufficient |

---

# 4. Domain dimensions

## 4.1 Soil

```text
SoilDepthClass
    SHALLOW
    MEDIUM_DEEP
    DEEP
    UNKNOWN
```

The old district source often combines `MEDIUM_DEEP` and `DEEP`.

## 4.2 Rainfall zone

```text
RainfallZone
    LOWER_RAINFALL_BHOOM_PARANDA
    OTHER_DHARASHIV
    UNKNOWN
```

## 4.3 Monsoon delay

```text
MonsoonDelayStage
    NORMAL_OR_LT_2_WEEKS
    ABOUT_2_WEEKS
    ABOUT_4_WEEKS
    ABOUT_6_WEEKS
    ABOUT_8_WEEKS
    UNKNOWN
```

These are source-aligned agricultural bands, not precise meteorological definitions.

## 4.4 Irrigation

```text
IrrigationAvailability
    RAINFED_ONLY
    PROTECTIVE_IRRIGATION_AVAILABLE
    RELIABLE_IRRIGATION
    UNKNOWN
```

## 4.5 Pre-sowing action

```text
CandidateAction
    KEEP_CANDIDATE
    KEEP_WITH_CONDITIONS
    COMPARE_ALTERNATIVE
    SUBSTITUTE_TO_SUPPORTED_OPTION
    RABI_PLANNING_OPTION
    NO_SUPPORTED_KHARIF_OPTION
    REVIEW_REQUIRED
```

---

# 5. First principle: preserve source alternatives

When the agricultural source says:

```text
fodder maize / fodder sorghum / keep fallow for Rabi
```

Pik Nirnay must not silently transform that into:

```text
PREPARE_FOR_RABI
```

unless Rabi planning is the only relevant source-backed option.

Instead retain:

```text
source_alternatives = [...]
v1_supported_alternatives = [...]
```

Example:

```text
source_alternatives = [
    FODDER_MAIZE,
    FODDER_SORGHUM,
    RABI_PLANNING
]

v1_supported_alternatives = [
    RABI_PLANNING
]

action = NO_SUPPORTED_KHARIF_OPTION
```

The UI may say that the source also lists alternatives outside the current Pik Nirnay crop set.

---

# 6. About two-week delayed onset

The older Dharashiv plan says "no change" for the normal crops listed across its major farming situations.

Recent VNMKV 2024 Marathwada guidance also allows soybean, pearl millet and pigeonpea into the first half of July when the monsoon is delayed by about 15 days, but reports yield reduction under delayed sowing.

## R-DHAR-ONSET-2W-SOY

```text
crop = SOYBEAN
delay = ABOUT_2_WEEKS
action = KEEP_WITH_CONDITIONS
evidence = CORROBORATED
```

Conditions:
- establishment moisture adequate,
- delay warning displayed.

## R-DHAR-ONSET-2W-PP

```text
crop = PIGEONPEA
delay = ABOUT_2_WEEKS
action = KEEP_WITH_CONDITIONS
evidence = CORROBORATED
```

## R-DHAR-ONSET-2W-PM

```text
crop = PEARL_MILLET
delay = ABOUT_2_WEEKS
where crop is relevant to the farming situation
action = KEEP_WITH_CONDITIONS
evidence = CORROBORATED
```

## R-DHAR-ONSET-2W-BG

```text
crop = BLACK_GRAM
delay = ABOUT_2_WEEKS
action = KEEP_WITH_CONDITIONS
evidence = LEGACY_DISTRICT_SPECIFIC
```

### Important black-gram caveat

The recent VNMKV 2024 delayed-monsoon recommendation names **green gram**, not black gram, in the 15-day delayed crop set.

The black-gram rule therefore remains prototype-only and depends mainly on the older Dharashiv plan.

---

# 7. About four-week delayed onset

This is where the revised A4 differs materially from V0.1.

Recent VNMKV 2024 guidance says that under approximately one-month delayed monsoon, soybean and pigeonpea may still be sown through the second half of July, albeit with around 40% yield reduction in the studied dryland situation.

Older Dharashiv guidance moves soybean toward soybean+pigeonpea earlier.

Therefore soybean cannot be treated as an automatic substitution rule.

## R-DHAR-ONSET-4W-PP

```text
crop = PIGEONPEA
delay = ABOUT_4_WEEKS
action = KEEP_WITH_CONDITIONS
evidence = CORROBORATED
```

Requirements:
- suitable current-duration variety,
- delay downside shown.

## R-DHAR-ONSET-4W-BG

```text
crop = BLACK_GRAM
delay = ABOUT_4_WEEKS
action = SUBSTITUTE_TO_SUPPORTED_OPTION
target = SOYBEAN_PIGEONPEA
evidence = LEGACY_DISTRICT_SPECIFIC
```

The substitution appears consistently in the old district table.

Because no newer delayed-sowing black-gram rule was found, label this clearly as legacy district guidance.

## R-DHAR-ONSET-4W-SOY

```text
crop = SOYBEAN
delay = ABOUT_4_WEEKS
action = COMPARE_ALTERNATIVE
alternative = SOYBEAN_PIGEONPEA
evidence = REVIEW_REQUIRED
```

Reason:

- legacy Dharashiv plan: shift to soybean+pigeonpea,
- VNMKV 2024: soybean may still be sown under one-month delay,
- 2022/2023 Maharashtra contingency discussions also allowed later soybean under exceptional conditions.

Therefore:

```text
DO NOT auto-remove sole soybean.
DO compare it against soybean+pigeonpea.
DO show strong delayed-sowing downside.
```

## R-DHAR-ONSET-4W-PM

```text
crop = PEARL_MILLET
soil = SHALLOW
delay = ABOUT_4_WEEKS
action = KEEP_WITH_CONDITIONS
evidence = LEGACY_DISTRICT_SPECIFIC
```

---

# 8. About six-week delayed onset — late July

## 8.1 Pigeonpea

### R-DHAR-ONSET-6W-PP-MD

```text
crop = PIGEONPEA
soil in {MEDIUM_DEEP, DEEP}
rainfall_zone = OTHER_DHARASHIV
delay = ABOUT_6_WEEKS
action = KEEP_WITH_CONDITIONS
evidence = LEGACY_DISTRICT_SPECIFIC
```

### R-DHAR-ONSET-6W-PP-SH

```text
crop = PIGEONPEA
soil = SHALLOW
delay = ABOUT_6_WEEKS
action = SUBSTITUTE_TO_SUPPORTED_OPTION
target = PEARL_MILLET_PIGEONPEA
evidence = LEGACY_DISTRICT_SPECIFIC
```

Applies in both assured-rainfall and Bhoom/Paranda shallow-soil situations in the district table.

### R-DHAR-ONSET-6W-PP-LOWRF-MD

```text
crop = PIGEONPEA
soil in {MEDIUM_DEEP, DEEP}
rainfall_zone = LOWER_RAINFALL_BHOOM_PARANDA
delay = ABOUT_6_WEEKS
action = REVIEW_REQUIRED
evidence = LEGACY_DISTRICT_SPECIFIC
```

The source gives several alternatives:
- no change,
- pearl millet+pigeonpea,
- sesame,
- fodder sorghum.

Do not collapse these to one automatic recommendation.

---

## 8.2 Black gram

### R-DHAR-ONSET-6W-BG-MD-ASSURED

```text
crop = BLACK_GRAM
soil in {MEDIUM_DEEP, DEEP}
rainfall_zone = OTHER_DHARASHIV
delay = ABOUT_6_WEEKS
action = SUBSTITUTE_TO_SUPPORTED_OPTION
target = PEARL_MILLET_PIGEONPEA
evidence = LEGACY_DISTRICT_SPECIFIC
```

The source also recommends protective irrigation where possible.

### R-DHAR-ONSET-6W-BG-SH-ASSURED

```text
crop = BLACK_GRAM
soil = SHALLOW
rainfall_zone = OTHER_DHARASHIV
delay = ABOUT_6_WEEKS
action = NO_SUPPORTED_KHARIF_OPTION
evidence = PRODUCT_DERIVED
```

Source alternatives:

```text
FODDER_MAIZE
FODDER_SORGHUM
RABI_PLANNING
```

Only Rabi planning is within current V1 decision scope.

### R-DHAR-ONSET-6W-BG-MD-LOWRF

```text
crop = BLACK_GRAM
soil in {MEDIUM_DEEP, DEEP}
rainfall_zone = LOWER_RAINFALL_BHOOM_PARANDA
delay = ABOUT_6_WEEKS
action = RABI_PLANNING_OPTION
evidence = LEGACY_DISTRICT_SPECIFIC
```

The district source explicitly says keep fallow and plan Rabi.

### R-DHAR-ONSET-6W-BG-SH-LOWRF

```text
crop = BLACK_GRAM
soil = SHALLOW
rainfall_zone = LOWER_RAINFALL_BHOOM_PARANDA
delay = ABOUT_6_WEEKS
action = NO_SUPPORTED_KHARIF_OPTION
evidence = PRODUCT_DERIVED
```

Source alternatives:
- fodder maize,
- fodder sorghum,
- keep fallow / plan Rabi.

---

## 8.3 Soybean

The old district plan changes sole soybean to soybean+pigeonpea.

However, newer Maharashtra evidence is more permissive about late-July soybean.

### R-DHAR-ONSET-6W-SOY

```text
crop = SOYBEAN
delay = ABOUT_6_WEEKS
where soybean is listed in the source farming situation
action = COMPARE_ALTERNATIVE
alternative = SOYBEAN_PIGEONPEA
evidence = REVIEW_REQUIRED
```

Interpretation:

- do not present late-July sole soybean as normal,
- do not automatically remove it,
- strongly surface soybean+pigeonpea,
- show that current/modern regional evidence still allows late soybean in exceptional delayed-monsoon contexts, but with substantial downside.

For V1 prototype, this is a **conflict-aware comparison rule**.

---

## 8.4 Pearl millet

### R-DHAR-ONSET-6W-PM

```text
crop = PEARL_MILLET
soil = SHALLOW
delay = ABOUT_6_WEEKS
action = KEEP_WITH_CONDITIONS
evidence = CORROBORATED
```

This is supported by:

- the old district table in applicable shallow-soil situations,
- VNMKV research specifically supporting late-sown pearl millet around late July.

---

# 9. About eight-week delayed onset — second week August

## 9.1 Pigeonpea

### R-DHAR-ONSET-8W-PP

```text
crop = PIGEONPEA
delay = ABOUT_8_WEEKS
action = SUBSTITUTE_TO_SUPPORTED_OPTION
target = PEARL_MILLET_PIGEONPEA
evidence = LEGACY_DISTRICT_SPECIFIC
variety_requirement = EARLY_OR_SHORT_DURATION_REQUIRED
```

The district plan repeats this transition across its main soil/rainfall situations.

Broader VNMKV dryland contingency work also identifies Bajra+Pigeonpea as an exceptional late-sowing system into early August, which provides directional corroboration.

---

## 9.2 Black gram

### R-DHAR-ONSET-8W-BG

```text
crop = BLACK_GRAM
delay = ABOUT_8_WEEKS
action = NO_SUPPORTED_KHARIF_OPTION
evidence = PRODUCT_DERIVED
```

Source alternatives across the district table:

```text
NIGER
FODDER_SORGHUM
KHARIF_FALLOW_FOR_RABI
```

Pik Nirnay must retain these source alternatives in provenance.

The product may display:

> No currently supported V1 Kharif crop replacement is selected from this rule. The source includes fodder/Niger or leaving the field for Rabi.

Do not translate this into a mandatory Rabi recommendation.

---

## 9.3 Soybean

### R-DHAR-ONSET-8W-SOY

```text
crop = SOYBEAN
delay = ABOUT_8_WEEKS
where soybean is listed in the district table
action = RABI_PLANNING_OPTION
evidence = LEGACY_DISTRICT_SPECIFIC
```

The district plan explicitly says:

```text
Kharif fallow followed by Rabi crops
```

This is therefore stronger than the black-gram interpretation.

---

## 9.4 Pearl millet

### R-DHAR-ONSET-8W-PM

```text
crop = PEARL_MILLET
soil = SHALLOW
delay = ABOUT_8_WEEKS
action = KEEP_WITH_CONDITIONS
evidence = LEGACY_DISTRICT_SPECIFIC
```

The old district plan retains sole pearl millet in the applicable shallow-soil situations.

Because modern general guidance this late is limited, V1 should carry a legacy-source warning.

---

## 9.5 Soybean + pigeonpea

Broader VNMKV contingency research lists soybean+pigeonpea among systems usable in exceptional situations into the first half of August, while Dharashiv's old sole-soybean rule says fallow/Rabi at about eight weeks.

### R-DHAR-ONSET-8W-SP

```text
crop = SOYBEAN_PIGEONPEA
delay = ABOUT_8_WEEKS
action = REVIEW_REQUIRED
evidence = REVIEW_REQUIRED
```

Do not automatically recommend this system in August.

---

# 10. Unknown context

## R-DHAR-CONTEXT-UNKNOWN

When a rule needs soil or rainfall zone and that input is unknown:

```text
action = REVIEW_REQUIRED
```

Do not substitute the district majority soil type.

Rules independent of the unknown field may still execute.

---

# 11. Protective irrigation

Protective irrigation is a **modifier**, not a date extension and not a universal crop rescue.

```text
if protective_irrigation_available:
    attach_mitigation(PROTECTIVE_IRRIGATION)
```

Only do this where the source recommends it.

Never implement:

```text
extend_sowing_window_by_n_days()
```

or:

```text
override_substitution_rule()
```

merely because irrigation exists.

---

# 12. Scenario advisories — separate from candidate rules

The following evidence is useful, but it belongs to `SCENARIO_ADVISORY`, not to pre-sowing candidate filtering.

---

## 12.1 Prolonged dry spell

The Dharashiv plan describes a mid-season long dry spell as roughly a consecutive two-week rainless period and lists measures such as:

- protective/life-saving irrigation where possible,
- interculture / soil mulch,
- conservation furrows,
- crop-residue mulch,
- delay of fertilizer top-dressing until moisture returns,
- crop/stage-specific foliar measures.

### Important limitation

The source's printed rainfall-threshold wording is ambiguous.

Therefore V1 must not yet implement a numeric dry-spell detector from this old table.

Use:

```text
ScenarioAdvisory
    scenario = PROLONGED_DRY_SPELL
```

until the weather-data work defines a current, defensible detection algorithm.

### Ranking prohibition

These management recommendations do **not** prove that one V1 crop is safer than another.

Do not turn them directly into comparative risk weights.

---

## 12.2 Terminal drought / early monsoon withdrawal

The district plan gives crop-management and Rabi-planning responses such as:

- life-saving irrigation,
- harvest at physiological maturity,
- Rabi planning for some crop/situation combinations.

Use this as:

```text
ScenarioAdvisory
    scenario = EARLY_MONSOON_WITHDRAWAL
```

Do not infer a crop-failure probability.

Do not automatically rank crops from this table alone.

---

## 12.3 Short-span heavy rain / waterlogging

The district plan says that under continuous high rainfall leading to waterlogging:

- soybean,
- pigeonpea,
- short-duration pulses

should have excess water drained at crop stages.

Recent 2024/2025 Maharashtra contingency meetings also emphasize drainage/BBF for excess-rain situations.

Use:

```text
ScenarioAdvisory
    scenario = HEAVY_RAIN_WATERLOGGING
    mitigation = DRAIN_EXCESS_WATER
```

### Important limitation

A2 soil depth does not define drainage.

Do not infer:

```text
DEEP => waterlogging risk
SHALLOW => no waterlogging risk
```

without a separate drainage field/evidence.

---

# 13. Candidate generation before scoring

The decision engine should operate in stages.

```text
FarmContext
    ↓
A3 timing assessment
    ↓
A4 candidate rules
    ↓
Eligible / conditional / substituted options
    ↓
Only then:
climate + financial comparison
```

Example:

```text
location = Tuljapur
soil = SHALLOW
monsoon_delay = ABOUT_6_WEEKS

SOYBEAN
    -> compare strongly against SOYBEAN_PIGEONPEA

BLACK_GRAM
    -> no V1 Kharif replacement from source;
       source also gives fodder/Rabi alternatives

PIGEONPEA
    -> substitute to PEARL_MILLET_PIGEONPEA

PEARL_MILLET
    -> keep with conditions

SOYBEAN_PIGEONPEA
    -> candidate

PEARL_MILLET_PIGEONPEA
    -> candidate
```

The later financial model must not make an agronomically excluded option look attractive merely because its historical market price is high.

---

# 14. Proposed rule contract

```text
DecisionRule
    rule_id
    version
    rule_family
    evidence_class
    source_ids[]
    conditions
    action
    target_crop_system?
    source_alternatives[]
    v1_supported_alternatives[]
    required_conditions[]
    mitigations[]
    warnings[]
    explanation_key
    status
```

Recommended `rule_family`:

```text
PRE_SOWING_CANDIDATE_RULE
SCENARIO_ADVISORY
```

Recommended status:

```text
ACTIVE_PROTOTYPE
REVIEW_REQUIRED
DEFERRED
```

---

# 15. Rules that must NOT be implemented yet

Do not implement:

- numeric LOW/MEDIUM/HIGH climate score,
- crop-failure probability,
- farmer-specific percentage yield reduction,
- one universal rainfall threshold for "monsoon onset",
- exact dry-spell detector from the legacy threshold wording,
- exact heavy-rain detector,
- automatic drainage classification,
- current seed-variety names copied from the 2011 plan,
- automatic August soybean+pigeonpea recommendation,
- black-gram late-sowing rules presented as current field-validated advice.

---

# 16. Evidence register

## E-A4-01 — ICAR-CRIDA Osmanabad/Dharashiv district contingency plan

Primary detailed district source for:
- delayed onset at ~2/4/6/8 weeks,
- soil/rainfall-zone distinctions,
- crop/system substitutions,
- dry-spell management,
- terminal drought,
- high-rainfall/waterlogging measures.

Source:  
https://www.icar-crida.res.in/CP-2012/statewiseplans/Maharastra(Pdf)/MAU,%20Parbhani/Maharashtra%2030-Osmanabad-%2031-12-2011.pdf

**Caution:** legacy district plan; variety names and some crop choices require current revalidation.

## E-A4-02 — VNMKV AICRP Dryland Agriculture, June 2024

Recent Marathwada evidence:
- ~15-day delayed monsoon: several crops including soybean, pearl millet and pigeonpea remain sowable into first half July, with yield penalties.
- ~30-day delayed monsoon: soybean and pigeonpea may extend into second half July, with large reported yield reduction under studied dryland conditions.

Source:  
https://www.vnmkv.ac.in/Content/Home/pdf/research/Dryland_Recommendation_All_24.07.2024.pdf

## E-A4-03 — VNMKV Decadal Research Achievements in Dryland Farming

Regional contingency-planning evidence includes:
- soybean+pigeonpea,
- bajra+pigeonpea,
- exceptional first-half-August cropping-system options.

Source:  
https://www.vnmkv.ac.in/Content/Home/pdf/research/Decadal_Research_Achivements_in_dryland_farming.pdf

## E-A4-04 — ICAR Maharashtra contingency preparedness, 2022

State expert recommendation allowed soybean approximately up to 25 July and explicitly called for weekly yield-decline evidence under delayed sowing.

Source:  
https://www.icar.gov.in/en/state-level-interface-meeting-agricultural-contingency-preparedness-maharashtra-2022-organized

## E-A4-05 — ICAR Maharashtra contingency preparedness, 2023

State discussion concluded soybean could be sown through July-end in the contingency context, with intercropping suggested after 15 July.

Source:  
https://www.icar.gov.in/hi/virtual-interface-meeting-enhancing-preparedness-agricultural-contingencies-kharif-2023-maharashtra

## E-A4-06 — ICAR-CRIDA Maharashtra contingency meeting, 2024/2025

Recent meetings emphasize:
- alternative crop/variety preparedness,
- BBF/drainage for excess rainfall,
- short-term rainfall forecasts and waterlogging management.

Sources:  
https://www.icar-crida.res.in/kharif-2024-for-Maharashtra.html  
https://www.icar-crida.res.in/Interface-meeting.html

---

# 17. Review conclusions

The A4 review makes four important corrections to V0.1:

1. **Late-July soybean is conflict-aware, not automatically substituted.**
2. **Black-gram fodder/Niger/Rabi alternatives are preserved rather than collapsed into Rabi.**
3. **Post-sowing climate-management evidence is separated from pre-sowing candidate rules.**
4. **Legacy district rules carry explicit source-age/evidence classification.**

---

# 18. A4 exit status

**Status: READY TO FREEZE FOR THE RESEARCH PROTOTYPE**, subject to product-owner approval.

It is **not** field-validation complete.

Before any real-farmer deployment, at minimum:
- current Dharashiv KVK/VNMKV validation,
- current variety review,
- current rainfall/monsoon-detection rules,
- and field usability testing
would still be required.

---

# 19. Next dependency

After A4 is frozen:

```text
C4 Evidence Register
    ↓
C1 FarmContext
C2 CropProfile
C3 DecisionRule
```

These domain structures can be implemented before Phase B data-provider integrations.

Phase B must be completed before the final decision engine uses live weather, climate history and market data.
