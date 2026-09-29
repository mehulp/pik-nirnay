# Pik Nirnay — C1 Assessment / Farm Context Domain Model

**Project:** Pik Nirnay / पीक निर्णय  
**Workstream:** C1 — FarmContext  
**Version:** V0.2 — reviewed  
**Status:** READY TO FREEZE FOR V1  
**Scope:** Normalized inputs for Dharashiv Kharif V1 pre-sowing assessment  
**Depends on:** A1–A4 + Evidence Register V0.2

---

## 1. Review conclusion

The V0.1 model was directionally correct but mixed three different kinds of information:

1. relatively stable field/farm facts,
2. the farmer's current sowing intent,
3. time-varying season/weather-derived state.

V0.2 separates these while preserving one object that the later decision engine can consume.

The revised top-level model is:

```text
AssessmentContext
├── assessment_date
├── season
├── farm
│   ├── location
│   ├── soil
│   └── water
├── sowing_intent
└── season_context
```

This separation is important for Phase B and historical replay.

---

# 2. Top-level model

```text
AssessmentContext
    assessment_date
    season
    farm
    sowing_intent
    season_context
```

`AssessmentContext` is the complete normalized input to A3/A4 evaluation.

`FarmContext` is now deliberately narrower.

---

# 3. Season

```text
Season
    KHARIF
```

V1 supports only Kharif.

An explicit season field prevents Kharif A3/A4 rules from accidentally being reused for Rabi later.

Do not infer the season solely from the calendar month.

---

# 4. Assessment date

```text
assessment_date: date
```

Meaning:

> The date for which this assessment is being made.

Why this is needed:

- provider-derived climate values can become stale,
- historical replay needs a reproducible "as-of" date,
- the same field and proposed sowing date may be evaluated under different historical contexts.

This is a domain timestamp, not a database `created_at`.

---

# 5. FarmContext

```text
FarmContext
├── LocationContext
├── SoilContext
└── WaterContext
```

FarmContext should contain facts that can be reused across multiple sowing-date or weather scenarios.

It must not contain crop recommendations or provider-specific schemas.

---

# 6. LocationContext

```text
LocationContext
    district
    taluka
    village_name?
    rainfall_zone
    rainfall_zone_source
```

## 6.1 District

```text
District
    DHARASHIV
```

V1 rules are district-specific.

---

## 6.2 Taluka

Because taluka affects A4 rainfall-context rules, it should be typed rather than free text.

Recommended enum:

```text
Taluka
    DHARASHIV
    TULJAPUR
    OMERGA
    LOHARA
    KALLAM
    BHOOM
    PARANDA
    WASHI
    UNKNOWN
```

Input normalization may accept spelling aliases such as:

```text
Osmanabad  -> DHARASHIV
Bhum       -> BHOOM
Bhoom      -> BHOOM
Kalamb     -> KALLAM
Kallamb    -> KALLAM
Umarga     -> OMERGA
Omerga     -> OMERGA
```

Aliases belong to an input/location resolver, not to agronomic rules.

---

## 6.3 Village

```text
village_name: Optional[str]
```

Village is informational in C1.

No A3/A4 rule may depend directly on arbitrary free-text village name.

A later geocoder/location resolver may normalize it.

---

## 6.4 RainfallZone

```text
RainfallZone
    LOWER_RAINFALL_BHOOM_PARANDA
    OTHER_DHARASHIV
    UNKNOWN
```

This remains a Pik Nirnay rule-input abstraction derived from the legacy Dharashiv contingency plan.

For V1, rainfall zone should normally be **derived**, not manually entered by the farmer.

Expected mapping:

```text
BHOOM   -> LOWER_RAINFALL_BHOOM_PARANDA
PARANDA -> LOWER_RAINFALL_BHOOM_PARANDA

other known Dharashiv talukas
        -> OTHER_DHARASHIV

UNKNOWN -> UNKNOWN
```

This mapping must live in a small reviewed resolver.

Do not duplicate this logic inside UI components or individual crop rules.

---

## 6.5 ContextSource

Common provenance enum:

```text
ContextSource
    USER_REPORTED
    RULE_DERIVED
    GIS_SUGGESTED
    FIELD_MEASURED
    PROVIDER_DERIVED
    UNKNOWN
```

For rainfall zone in V1 the usual source will be:

```text
RULE_DERIVED
```

---

# 7. SoilContext

```text
SoilContext
    depth_class
    source
    observed_depth_cm?
```

## 7.1 SoilDepthClass

```text
SoilDepthClass
    SHALLOW
    MEDIUM_DEEP
    DEEP
    UNKNOWN
```

These categories are frozen for V1.

The numeric boundaries are not.

---

## 7.2 Observed depth

```text
observed_depth_cm: Optional[float]
```

The field was renamed from `raw_depth_cm` because it represents an observation, not necessarily unprocessed machine data.

Valid examples:

```text
observed_depth_cm = 42
depth_class = UNKNOWN
```

or:

```text
observed_depth_cm = 42
depth_class = SHALLOW
source = FIELD_MEASURED
```

The second form means the category came from some independent approved classification/observation.

C1 must not itself execute:

```text
42 cm -> SHALLOW
```

until the numeric classification rule is approved.

Validation:

```text
observed_depth_cm is None
OR observed_depth_cm > 0
```

---

# 8. WaterContext

```text
WaterContext
    irrigation_availability
    source
```

## IrrigationAvailability

```text
IrrigationAvailability
    RAINFED_ONLY
    PROTECTIVE_IRRIGATION_AVAILABLE
    RELIABLE_IRRIGATION
    UNKNOWN
```

Meanings:

### RAINFED_ONLY
No realistic life-saving/protective irrigation is available.

### PROTECTIVE_IRRIGATION_AVAILABLE
Limited irrigation can be supplied during a critical stress event.

### RELIABLE_IRRIGATION
A dependable water source exists beyond occasional protective irrigation.

This is representable even though the primary V1 persona is rain-fed/limited irrigation.

### UNKNOWN
Do not silently interpret missing information as rain-fed.

---

# 9. SowingIntent

The farmer's proposed action should not be stored as a stable farm fact.

```text
SowingIntent
    decision_type
    proposed_sowing_date
```

## DecisionType

```text
DecisionType
    FIRST_SOWING
    RESOWING
```

V1 decision rules support only:

```text
FIRST_SOWING
```

`RESOWING` is intentionally representable so the application can say:

```text
UNSUPPORTED_DECISION_TYPE
```

instead of accidentally applying first-sowing logic.

That policy check belongs above the FarmContext model.

---

## Proposed sowing date

```text
proposed_sowing_date: date
```

Exact date must be retained.

C1 must not reject dates outside A3 windows.

A3 needs to be able to return:

```text
OUTSIDE_V1_WINDOW
```

---

# 10. SeasonContext

Time-varying climate/season state belongs here rather than in FarmContext.

```text
SeasonContext
    monsoon_delay_stage
    monsoon_delay_days?
    monsoon_delay_source

    sowing_moisture_status
    moisture_status_source

    as_of_date
```

`as_of_date` should normally equal the date to which these derived season facts refer.

This makes provider-derived values usable for historical replay and staleness checks.

---

# 11. MonsoonDelayStage

```text
MonsoonDelayStage
    NORMAL_OR_LT_2_WEEKS
    ABOUT_2_WEEKS
    ABOUT_4_WEEKS
    ABOUT_6_WEEKS
    ABOUT_8_WEEKS
    UNKNOWN
```

A4 consumes this normalized state.

C1 must not invent exact numeric boundaries for `ABOUT`.

---

## Observed/derived delay days

```text
monsoon_delay_days: Optional[int]
```

Validation:

```text
None
OR >= 0
```

No automatic conversion:

```text
days -> stage
```

until a reviewed resolver is approved.

If both values are present, C1 does not attempt to prove they are consistent.

The resolver/provider that produced them owns that consistency.

---

# 12. SowingMoistureStatus

```text
SowingMoistureStatus
    READY
    NOT_READY
    UNKNOWN
```

The field belongs in `SeasonContext` because it changes with rainfall/weather rather than being a stable farm property.

A3/A4 established:

```text
calendar_window != permission_to_sow
```

C1 stores the normalized status but does not calculate it.

Default for early implementation:

```text
UNKNOWN
```

---

# 13. Why Phase B fits cleanly now

Phase B can later produce dynamic facts without mutating the farm model:

```text
Weather / climate provider
        ↓
provider adapter
        ↓
normalized observations
        ↓
reviewed derivation rules
        ↓
SeasonContext
```

The same:

```text
FarmContext
```

can therefore be evaluated for:

- today's sowing decision,
- a different proposed sowing date,
- a historical 2023 replay,
- a different weather-provider implementation.

This is preferable to embedding Open-Meteo fields in `FarmContext`.

---

# 14. Proposed Python/Pydantic shape

Illustrative:

```python
class AssessmentContext(BaseModel):
    assessment_date: date
    season: Season
    farm: FarmContext
    sowing_intent: SowingIntent
    season_context: SeasonContext
```

```python
class FarmContext(BaseModel):
    location: LocationContext
    soil: SoilContext
    water: WaterContext
```

```python
class LocationContext(BaseModel):
    district: District
    taluka: Taluka
    village_name: str | None = None
    rainfall_zone: RainfallZone
    rainfall_zone_source: ContextSource
```

```python
class SoilContext(BaseModel):
    depth_class: SoilDepthClass
    source: ContextSource
    observed_depth_cm: float | None = None
```

```python
class WaterContext(BaseModel):
    irrigation_availability: IrrigationAvailability
    source: ContextSource
```

```python
class SowingIntent(BaseModel):
    decision_type: DecisionType
    proposed_sowing_date: date
```

```python
class SeasonContext(BaseModel):
    monsoon_delay_stage: MonsoonDelayStage
    monsoon_delay_days: int | None = None
    monsoon_delay_source: ContextSource

    sowing_moisture_status: SowingMoistureStatus
    moisture_status_source: ContextSource

    as_of_date: date
```

---

# 15. UNKNOWN remains first-class

```text
UNKNOWN != district average
UNKNOWN != rain-fed
UNKNOWN != error
UNKNOWN != zero
```

Examples:

### Unknown taluka

```text
taluka = UNKNOWN
rainfall_zone = UNKNOWN
```

A4 zone-dependent rules cannot execute automatically.

### Unknown soil

```text
depth_class = UNKNOWN
```

Soil-dependent A4 rules cannot execute automatically.

### Unknown monsoon delay

A3 may still evaluate calendar timing.

A4 delayed-onset rules cannot be treated as confirmed.

### Unknown sowing moisture

The product may compare contextual crop exposure, but must not issue a "sow now" instruction.

---

# 16. Validation C1 may implement

Safe structural validation:

```text
season == KHARIF

district == DHARASHIV

observed_depth_cm is None
OR observed_depth_cm > 0

monsoon_delay_days is None
OR monsoon_delay_days >= 0

proposed_sowing_date is a valid date

as_of_date is a valid date

all enum values are valid
```

---

# 17. Validation C1 must not implement

Do not implement inside these models:

```text
observed_depth_cm -> SoilDepthClass

monsoon_delay_days -> MonsoonDelayStage

weather observations -> SowingMoistureStatus

crop recommendation logic

risk scoring
```

---

# 18. Location resolver

One small deterministic resolver is justified after C1:

```text
resolve_rainfall_zone(taluka)
```

Expected V1 behavior:

```text
BHOOM, PARANDA
    -> LOWER_RAINFALL_BHOOM_PARANDA

DHARASHIV, TULJAPUR, OMERGA, LOHARA,
KALLAM, WASHI
    -> OTHER_DHARASHIV

UNKNOWN
    -> UNKNOWN
```

The resolver should be unit-tested and should write:

```text
rainfall_zone_source = RULE_DERIVED
```

This is location normalization, not crop recommendation logic.

---

# 19. Example assessment

```text
assessment_date = 2027-07-27
season = KHARIF

farm:
    location:
        district = DHARASHIV
        taluka = BHOOM
        rainfall_zone = LOWER_RAINFALL_BHOOM_PARANDA
        rainfall_zone_source = RULE_DERIVED

    soil:
        depth_class = MEDIUM_DEEP
        source = USER_REPORTED

    water:
        irrigation_availability = PROTECTIVE_IRRIGATION_AVAILABLE
        source = USER_REPORTED

sowing_intent:
    decision_type = FIRST_SOWING
    proposed_sowing_date = 2027-07-27

season_context:
    monsoon_delay_stage = ABOUT_6_WEEKS
    monsoon_delay_source = PROVIDER_DERIVED
    monsoon_delay_days = null

    sowing_moisture_status = READY
    moisture_status_source = PROVIDER_DERIVED

    as_of_date = 2027-07-27
```

This object still contains no crop recommendation.

---

# 20. Suggested implementation tests

Claude should eventually test:

1. complete valid assessment context,
2. all important UNKNOWN paths,
3. non-Dharashiv district rejected,
4. negative/zero observed soil depth rejected,
5. negative monsoon-delay days rejected,
6. exact sowing date preserved,
7. no soil-depth numeric classification occurs,
8. no monsoon-day classification occurs,
9. `RESOWING` can be represented,
10. application policy recognizes RESOWING as unsupported,
11. `BHOOM` resolves to lower-rainfall zone,
12. `PARANDA` resolves to lower-rainfall zone,
13. all other known Dharashiv talukas resolve to other-Dharashiv,
14. UNKNOWN taluka resolves to UNKNOWN zone,
15. serialization preserves provenance and `as_of_date`.

---

# 21. Decisions from V0.1 review

| Question | Frozen V1 decision |
|---|---|
| Taluka string or enum? | **Enum** — decision-critical and bounded to eight Dharashiv talukas |
| Keep observed soil depth? | **Yes**, optional and non-decisional |
| Keep monsoon-delay days? | **Yes**, optional |
| Keep sowing-moisture status before algorithm exists? | **Yes**, in `SeasonContext`, default UNKNOWN |
| Represent RESOWING? | **Yes**, recognized but unsupported by V1 rules |
| Farm + dynamic climate in one object? | **No** — separate `FarmContext` and `SeasonContext` |
| Add assessment/as-of date? | **Yes**, needed for replay/staleness |
| Explicit season? | **Yes — KHARIF** |

---

# 22. What is deliberately deferred

C1 does not yet define:

- soil depth numeric classifier,
- effective monsoon-onset algorithm,
- monsoon-delay-day classifier,
- sowing-moisture algorithm,
- geocoding,
- live weather fields,
- market data,
- drainage condition,
- crop profile,
- decision rules,
- risk score.

Those belong to later reviewed nodes.

---

# 23. C1 freeze decision

**Status: `READY_TO_FREEZE` for V1 domain modelling.**

The model now cleanly separates:

```text
stable farm facts
+
farmer sowing intent
+
time-varying season facts
```

while remaining provider-independent and compatible with Phase B and historical replay.
