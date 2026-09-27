# Pik Nirnay — V1 Project Execution Graph

## 1. Objective

Build a working prototype of Pik Nirnay that can answer one narrowly defined question:

> For a rain-fed Kharif farmer in Dharashiv, given soil depth, sowing date, irrigation availability, weather/climate conditions and approximate financial exposure, how do a small number of locally valid crop or cropping-system choices compare in terms of risk?

V1 is a research-backed prototype and system-design learning project.

It is not yet intended to provide production agricultural advice.

## 2. High-Level Project Graph

```text
                         PIK NIRNAY V1
                               │
          ┌────────────────────┴────────────────────┐
          │                                         │
          ↓                                         ↓
    DOMAIN KNOWLEDGE                          DATA FOUNDATION
          │                                         │
    ┌─────┼─────────┐                    ┌──────────┼───────────┐
    ↓     ↓         ↓                    ↓          ↓           ↓
 Crops   Soil    Agronomy             Weather    Climate     Market
              /contingency              API      history      data
                    │                    │          │           │
                    └────────────┬───────┴──────────┴───────────┘
                                 ↓
                         NORMALIZED DOMAIN MODEL
                                 │
                                 ↓
                         DECISION RULE MATRIX
                                 │
                                 ↓
                         DECISION ENGINE V1
                                 │
                ┌────────────────┼─────────────────┐
                ↓                ↓                 ↓
            Risk logic      Explainability    Provenance
                │                │                 │
                └────────────────┼─────────────────┘
                                 ↓
                       SCENARIO / REPLAY ENGINE
                                 │
                                 ↓
                         API / APPLICATION LAYER
                                 │
                  ┌──────────────┴──────────────┐
                  ↓                             ↓
             Marathi UX                    English UX
                  │                             │
                  └──────────────┬──────────────┘
                                 ↓
                       END-TO-END V1 PROTOTYPE
                                 │
                                 ↓
                        HISTORICAL VALIDATION
                                 │
                                 ↓
                             V1 DONE
```

## 3. Workstreams

| ID | Workstream | Purpose | Primary Owner |
|---|---|---|---|
| W1 | Dharashiv domain research | Establish crops, soil conditions, sowing windows and contingency guidance | ChatGPT + Mehul |
| W2 | Data foundation | Establish weather, historical climate and market data integrations | ChatGPT design + Claude execution |
| W3 | Domain model | Convert research/data requirements into software-owned contracts | ChatGPT + Claude |
| W4 | Decision engine | Implement explainable crop-risk comparison | ChatGPT rules + Claude execution |
| W5 | UX | Marathi-first farmer decision flow | ChatGPT + Mehul + Claude |
| W6 | Validation | Test scenarios and historical seasons | ChatGPT + Claude |

## 4. Phase A — Domain Discovery

### A1 — Dharashiv Crop Shortlist

**Goal**

Identify the limited set of crops and cropping systems supported in V1.

Potential starting candidates:

- Soybean
- Tur / pigeonpea
- Soybean + Tur intercropping
- Bajra
- Jowar

These are candidates only until research is completed.

**Owner**

ChatGPT + Mehul

**Output**

`docs/research/dharashiv-crops.md`

**Exit criteria**

Each V1 crop has:

- reason for inclusion
- relevant soil types
- expected sowing window
- approximate crop duration
- irrigation dependency
- supporting source

**Dependency**

None.

### A2 — Dharashiv Soil Model

**Goal**

Define the soil abstraction used in V1.

Expected V1 model:

```text
SHALLOW_BLACK
MEDIUM_BLACK
DEEP_BLACK
UNKNOWN
```

For each category document:

- water-holding implications
- crop suitability
- dry-spell exposure
- limitations of farmer self-identification

**Owner**

ChatGPT + Mehul

**Output**

`docs/research/dharashiv-soils.md`

**Dependency**

None.

### A3 — Sowing Window Matrix

**Goal**

Establish normal and delayed sowing windows for each V1 crop.

Example structure:

```text
Crop
    Preferred window
    Acceptable delay
    Late sowing
    Severe delay
    Recommended alternative
```

**Owner**

ChatGPT

**Output**

`docs/research/sowing-windows.md`

**Dependency**

A1

### A4 — Climate Contingency Rules

**Goal**

Convert existing agricultural contingency guidance into structured rules.

Conditions include:

- delayed monsoon
- prolonged dry spell
- inadequate rainfall
- excessive rainfall
- limited irrigation
- late sowing

**Owner**

ChatGPT research + Mehul approval

**Output**

`docs/research/dharashiv-contingency-rules.md`

**Dependency**

A1 + A2 + A3

## 5. Phase B — Data Foundation

These nodes can partly run in parallel with Phase A.

### B1 — Weather Provider Contract

**Goal**

Define what Pik Nirnay needs from a weather provider without binding the system to Open-Meteo.

Possible normalized model:

```text
WeatherSnapshot
    location
    generated_at
    daily_forecast[]
    rainfall_mm
    min_temperature
    max_temperature
    precipitation_probability
```

**Owner**

ChatGPT design → Claude implementation

**Output**

- WeatherProvider contract
- normalized weather DTO
- tests

**Dependency**

PRD only.

### B2 — Open-Meteo Adapter

**Goal**

Implement V1 live weather integration.

**Owner**

Claude

**Output**

`OpenMeteoProvider`

with:

- API client
- validation
- normalization
- retries/timeouts where appropriate
- tests
- failure handling

**Dependency**

B1

### B3 — Historical Climate Provider

**Goal**

Support historical rainfall/climate queries for replay and risk context.

Likely providers:

- NASA POWER
- Open-Meteo historical API

Provider choice remains an implementation/design decision.

**Owner**

ChatGPT design → Claude execution

**Output**

HistoricalClimateProvider abstraction and implementation.

**Dependency**

B1

### B4 — Market Data Provider

**Goal**

Normalize mandi price information needed for risk calculations.

Initial required information:

```text
commodity
market
date
min_price
max_price
modal_price
```

Derived values may later include:

```text
median
25th percentile
price variability
recent trend
```

**Owner**

ChatGPT design → Claude execution

**Dependency**

None.

## 6. Phase C — Domain Model

### C1 — Farm Context Model

Represent farmer-entered decision inputs.

Example:

```text
FarmContext
    location
    area
    soil_depth
    irrigation_type
    sowing_date
    budget
```

**Owner**

ChatGPT design → Claude implementation

**Dependency**

A2

### C2 — Crop Profile Model

Represent relevant crop characteristics.

Example:

```text
CropProfile
    crop_id
    crop_name
    soil_compatibility
    sowing_window
    water_requirement
    drought_sensitivity
    excess_rain_sensitivity
    crop_duration
    approximate_input_cost
    supported_intercrops
```

**Owner**

ChatGPT defines semantics → Claude implements

**Dependency**

A1 + A3

### C3 — Rule Model

Create a software representation for decision rules.

Conceptually:

```text
DecisionRule
    rule_id
    version
    source
    conditions
    outcome
    explanation_key
    effective_from
    status
```

**Owner**

ChatGPT + Claude

**Dependency**

A4

### C4 — Evidence Register

Every important rule should point to its evidence.

Example:

```text
R-DHAR-KH-001
    Source:
    Page/section:
    Interpretation:
    Approved:
    Rule version:
```

**Owner**

ChatGPT

**Output**

`docs/research/evidence-register.md`

**Dependency**

A1–A4

## 7. Phase D — Decision Engine

This phase must **not start until the first rule matrix exists.**

### D1 — Hard Feasibility Filtering

Remove crop options clearly unsuitable under the supplied conditions.

Examples:

- incompatible soil
- sowing window exceeded
- irrigation requirement unavailable

**Owner**

Claude

**Input**

Approved rules.

### D2 — Climate Risk Evaluation

Evaluate conditions such as:

```text
dry_spell_risk
delayed_sowing_risk
excess_rain_risk
water_availability_risk
```

Output should be categorical initially:

```text
LOW
MEDIUM
HIGH
```

No fake probabilistic precision.

**Owner**

Claude

### D3 — Financial Exposure

Initial calculations:

```text
estimated_input_cost
capital_at_risk
recent_price_range
historical_price_downside
```

This does not attempt to calculate guaranteed profit.

**Owner**

Claude

**Dependency**

B4 + Crop Profile data.

### D4 — Crop Risk Card Generator

Combine:

```text
Agronomic fit
        +
Climate exposure
        +
Input exposure
        +
Market exposure
```

Produce:

```text
CropRiskCard
```

containing:

```text
crop
risk_level
input_cost_range
climate_risks
market_risk
advantages
warnings
explanations
sources
data_freshness
```

**Owner**

Claude

**Dependency**

D1 + D2 + D3

### D5 — What-If Engine

Allow one input to change.

Example:

```text
No irrigation
      ↓
One protective irrigation
```

Re-run decision evaluation.

No separate intelligence is necessary.

The same deterministic engine should be reused.

**Owner**

Claude

**Dependency**

D4

## 8. Phase E — Explainability and Provenance

### E1 — Explanation Engine

Every result must answer:

> हे का दाखवले आहे?

Example:

```text
HIGH RISK

Because:

• shallow black soil
• no protective irrigation
• sowing date is late
• soybean has greater dry-spell exposure
```

**Owner**

ChatGPT wording + Claude implementation.

### E2 — Provenance

Expose or retain:

```text
weather source
market source
weather timestamp
market-data period
rules used
rule version
```

**Owner**

Claude

## 9. Phase F — Marathi-First UX

### F1 — Language Framework

Create localization framework.

```text
mr.json
en.json
```

No hard-coded UI language.

**Owner**

Claude.

### F2 — Farm Input Flow

Likely flow:

```text
Location
    ↓
Soil depth
    ↓
Farm area
    ↓
Irrigation
    ↓
Sowing date
    ↓
Budget
    ↓
Analyse
```

UX should require minimal typing.

### F3 — Crop Comparison Screen

Display approximately 3–4 options.

Example:

```text
सोयाबीन
Risk: HIGH

तूर
Risk: MEDIUM

सोयाबीन + तूर
Risk: MEDIUM

बाजरी
Risk: LOW
```

Actual labels depend on the approved domain rules.

### F4 — Explanation View

User selects:

> हे का दाखवले आहे?

and sees the conditions behind the result.

## 10. Phase G — Historical Validation

### G1 — Replay Framework

Allow execution using historical weather rather than current forecasts.

Example:

```text
Dharashiv
10 July 2023
Shallow black soil
Rain-fed
```

Engine must behave as though the future rainfall is unknown.

### G2 — Kharif 2023 Replay

Use the documented problematic Dharashiv season as the first scenario.

Check whether the recommendations appear reasonable given information available at sowing time.

### G3 — Additional Seasons

Replay several seasons with different rainfall patterns.

Purpose:

- find overly aggressive rules
- detect contradictory rules
- validate explanations
- test provider/data integration

Historical replay provides sanity checking, not scientific proof.

## 11. Phase H — End-to-End V1

V1 should support:

```text
User
 ↓
Marathi input
 ↓
FarmContext
 ↓
Weather / climate / market
 ↓
Decision rules
 ↓
Risk comparison
 ↓
Marathi explanation
 ↓
What-if scenario
```

## 12. V1 Completion Gate

V1 is complete when a user can:

1. choose Dharashiv location
2. use the application in Marathi
3. specify soil depth
4. specify acreage
5. specify irrigation availability
6. specify sowing date
7. optionally specify budget
8. receive 3–4 locally applicable crop/cropping-system options
9. see climate-risk classification
10. see approximate financial exposure
11. understand why each option received its classification
12. see source/data freshness
13. change irrigation or another supported input
14. recompute the scenario
15. run at least one historical Dharashiv replay

No additional feature is required to call the first prototype complete.

## 13. Ownership Model

```text
MEHUL
Product owner
Final scope/trade-off decisions
       │
       ↓
CHATGPT
Research
Analysis
PRD
Architecture discussion
Rule definition
Claude task specification
       │
       ↓
CLAUDE CODE
Implementation
Tests
Refactoring within scope
Verification
       │
       ↓
CHATGPT + MEHUL
Review
Learning
Next decision
```

Claude Code should not independently redefine the product or agricultural domain rules.

## 14. First Critical Path

The first critical path is:

```text
A1 Crop Shortlist
      ↓
A2 Soil Model
      ↓
A3 Sowing Windows
      ↓
A4 Contingency Rules
      ↓
C2 Crop Profiles
      ↓
C3 Rule Model
      ↓
D1/D2 Decision Engine
```

The data work can proceed partly in parallel:

```text
B1 Weather Contract
      ↓
B2 Open-Meteo

B3 Historical Climate

B4 Market Data
```

The two streams meet at the Decision Engine.

## 15. Rule for Starting Claude Implementation

Claude can begin infrastructure/data work before agricultural research is complete.

Claude **may begin**:

- repository setup
- modular-monolith skeleton
- localization framework
- provider abstractions
- Open-Meteo integration
- historical climate integration
- testing framework

Claude **must not yet implement**:

- crop recommendation logic
- risk classification rules
- soil/crop suitability logic
- delayed-sowing decisions
- financial risk interpretation

until approved rule definitions exist.
