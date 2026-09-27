# Pik Nirnay / पीक निर्णय

## Product Requirements Document

Marathi-first climate and financial risk decision support for pre-sowing crop choice in Dharashiv, Maharashtra

| **Version**           | 0.1 — First working PRD         |
|-----------------------|---------------------------------|
| **Date**              | 26 September 2026               |
| **Status**            | Draft / discovery-led prototype |
| **Initial geography** | Dharashiv district, Maharashtra |
| **Initial season**    | Kharif                          |

**Product intent**

**Help a rain-fed farmer compare a small number of locally realistic Kharif crop choices by making climate risk, agronomic fit and approximate financial downside visible before sowing.**

# 1. Document Purpose

This PRD defines the first buildable version of Pik Nirnay. It is intentionally narrow. The project is being developed first as a personal learning and portfolio project, using published agronomic guidance and public/open data. It is not yet intended for production use by farmers, and it does not claim to replace an agronomist, Krishi Vigyan Kendra (KVK), or official government advisory.

| **V1 question: “Given this field, this sowing date and the current weather/climate context, what are the farmer’s realistic crop choices and what downside risk does each choice carry?”** |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

# 2. Problem and Evidence Context

Dharashiv is a strong prototype geography because crop outcomes are materially affected by rainfall timing, soil water-holding capacity and access to protective irrigation. A 2024 PoCRA monitoring report describes 66.14% of Dharashiv’s geographical area as shallow black soil and documents a 48-day dry spell during the 2023 Kharif season; it also notes that rainfall distribution can damage crops even when seasonal totals appear less extreme. The district contingency plan published by ICAR-CRIDA contains crop- and soil-specific actions for delayed monsoon, dry spells and crop establishment failure. These sources make it possible to build an explainable prototype from documented rules rather than inventing recommendations.

The product hypothesis is that much agricultural information already exists, but it is fragmented across weather services, contingency plans, market-price datasets and expert guidance. Pik Nirnay will not attempt to create a new agricultural knowledge system; it will operationalize a narrow slice of existing knowledge at the pre-sowing decision point.

# 3. Product Objectives

| **Farmer-facing objective**                                                                                                                      | **Prototype objective**                                                                                                                     | **System-design objective**                                                                                                                                    |
|--------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Make trade-offs visible: agronomic fit, climate exposure, approximate cost exposure and price downside — not a single opaque “best crop” answer. | Demonstrate that a credible decision-support MVP can be built from public/open data and documented agronomic rules before field validation. | Practice provider abstractions, time-series ingestion, rule/scenario engines, caching, localization, provenance, observability and modular-monolith evolution. |

# 4. Goals and Non-Goals

| **In scope for V1**                                                          | **Explicitly out of scope for V1**                                            |
|------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| • Dharashiv district only; Kharif only.                                      | • No pan-India or pan-Maharashtra crop coverage.                              |
| • Rain-fed / limited-protective-irrigation farming situations.               | • No marketplace, input ordering, lending, insurance claims or payment flows. |
| • Small curated set of locally realistic crops and cropping systems.         | • No pest/disease photo diagnosis.                                            |
| • Marathi-first UX with English toggle.                                      | • No generic “ask anything about farming” chatbot.                            |
| • Current/recent weather plus historical climate context.                    | • No satellite-based field monitoring in V1.                                  |
| • Approximate input-cost exposure and historical mandi price behaviour.      | • No ML model that autonomously chooses the crop.                             |
| • Explainable rule/scenario engine with visible evidence and data freshness. | • No guaranteed yield, profit or price prediction.                            |
| • What-if comparison by changing one or more field assumptions.              | • No claim that the product prevents farmer distress or suicide.              |

# 5. Target User and V1 Assumptions

The initial user is a design persona, not a field-validated persona. These assumptions are intentionally explicit so they can be challenged later.

| **Dimension**     | **V1 assumption**                                                            | **Reason / product implication**                                      |
|-------------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| Geography         | Dharashiv district                                                           | Keeps agronomic and market context bounded.                           |
| Season            | Kharif                                                                       | Matches the main rainfall-risk decision window.                       |
| Farm situation    | Primarily rain-fed; optional protective irrigation                           | Water availability must materially influence risk.                    |
| Soil input        | Shallow / medium / deep black / unknown                                      | Avoids dependency on unreliable or unavailable field-level soil APIs. |
| Decision point    | Before sowing or delayed sowing                                              | Focuses the product on one high-value decision.                       |
| Field unit        | One field per analysis                                                       | Keeps V1 interaction and data model simple.                           |
| Candidate crops   | Approx. 3–5 options, including at least one cropping-system/intercrop option | Avoids generic recommendation across dozens of crops.                 |
| Language          | Marathi default; English optional                                            | Farmer-facing text must be understandable without English.            |
| Model             | Rules + scenario comparison                                                  | Supports explainability and agronomist review.                        |
| Validation status | Desk research + historical replay                                            | No field-effectiveness claim until validated.                         |

# 6. Core User Journey

| **Step** | **User action**        | **Product behaviour**                                                                                                                |
|----------|------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| 1        | Choose language        | Default to Marathi; English available for portfolio/demo usage.                                                                      |
| 2        | Select location        | Choose taluka/village within Dharashiv or allow device location later. V1 may use a curated location list.                           |
| 3        | Describe field         | Soil depth/type, acreage, irrigation availability, sowing date and approximate input budget.                                         |
| 4        | Fetch context          | System retrieves weather/forecast, recent rainfall and historical climate context; market data is read from cached/ingested sources. |
| 5        | Generate candidate set | Rules eliminate clearly unsuitable options and retain 3–4 locally realistic crops/cropping systems.                                  |
| 6        | Compare risk cards     | Each option shows agronomic fit, climate scenario sensitivity, approximate financial exposure, price context and reasons.            |
| 7        | Run a what-if          | User changes a variable such as sowing date or “one protective irrigation” and recomputes.                                           |
| 8        | See sources/freshness  | Each result exposes source category, last-updated timestamp and disclaimer.                                                          |

# 7. Functional Requirements

Priority notation: M = Must for V1, S = Should if time permits, C = Could later.

| **ID** | **P** | **Requirement**         | **Acceptance intent**                                                                                                         |
|--------|-------|-------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| FR-01  | M     | Language selection      | Default interface shall be Marathi, with a persistent Marathi/English toggle.                                                 |
| FR-02  | M     | Location selection      | User shall select a Dharashiv taluka/village from supported locations.                                                        |
| FR-03  | M     | Field inputs            | System shall capture soil class, acreage, irrigation availability, planned sowing date and approximate budget/budget band.    |
| FR-04  | M     | Weather context         | System shall retrieve current/recent weather and forecast data through a provider abstraction.                                |
| FR-05  | M     | Climate context         | System shall compute or retrieve historical rainfall/temperature context relevant to the selected location and sowing period. |
| FR-06  | M     | Candidate generation    | System shall produce a small set of locally valid crops/cropping systems based on documented eligibility rules.               |
| FR-07  | M     | Risk comparison         | System shall produce separate agronomic/climate/financial/price risk indicators for each candidate.                           |
| FR-08  | M     | Explanation             | Every recommendation/risk flag shall expose a “Why am I seeing this?” explanation based on rule inputs.                       |
| FR-09  | M     | Financial exposure      | System shall show approximate cost-at-risk / cost band and use historical mandi prices for downside context.                  |
| FR-10  | M     | What-if analysis        | User shall be able to change at least irrigation availability or sowing date and recompute.                                   |
| FR-11  | M     | Provenance              | Result screen shall show data source and freshness for weather/market data; rules shall have a source reference/version.      |
| FR-12  | M     | Safety disclaimer       | System shall state clearly that the output is decision support, not guaranteed agronomic or financial advice.                 |
| FR-13  | S     | Unknown soil assistance | If soil type is unknown, system should provide Marathi descriptions/illustrations and a conservative fallback.                |
| FR-14  | S     | Shareable result        | System should allow a compact risk-card summary to be shared/exported for demonstration.                                      |
| FR-15  | C     | Offline/read-only cache | Previously generated results may be accessible with a visible “stale data” marker.                                            |

# 8. Decision Engine Requirements

V1 shall use an explainable rule/scenario engine. It shall not output an uncalibrated “83% success probability” or similar precision that is not supported by the data.

## Processing sequence

1.  Apply hard eligibility constraints: geography, season, soil suitability, sowing window and minimum water assumptions.

2.  Generate locally valid crop/cropping-system candidates.

3.  Evaluate agronomic fit: soil depth, sowing date and irrigation.

4.  Evaluate climate exposure under at least three scenarios: broadly normal, dry-spell/delayed-rainfall and excess-rain conditions.

5.  Calculate approximate input exposure using configurable cost bands rather than false precision.

6.  Add price-risk context from recent historical mandi prices (median/range/low-percentile behaviour where data quality allows).

7.  Produce component risk flags and an overall exposure label (Low / Medium / High) using versioned, reviewable rules.

8.  Emit human-readable Marathi and English explanations referencing the factors that fired each rule.

## Conceptual crop profile

```text
CropProfile
  crop / cropping_system
  suitable_soil_depths
  normal_sowing_window
  latest_sowing_window
  water_requirement / protective_irrigation_effect
  drought_sensitivity
  excess_rain_sensitivity
  crop_duration
  approximate_input_cost_band
  expected_yield_reference_range
  contingency_rules
  supported_intercrops
  agronomy_source_id / rule_version
```

## Illustrative output dimensions

- Agronomic fit: suitable / conditional / unsuitable.

- Climate risk: low / medium / high, with scenario-specific reasons.

- Approximate input exposure: cost band per acre and total for entered acreage.

- Price context: recent median, recent low range/percentile and latest available mandi observation where reliable.

- Overall exposure: a rule-derived label that never hides the individual component risks.

- Explanation: plain-language reason plus source/freshness metadata.

# 9. Marathi-First UX and Localization

Marathi is a product requirement, not a translation task after V1. The information architecture, labels and explanations should be designed to be understandable in Marathi first; English mirrors the same keys for demonstration and developer use.

| **Concept key**    | **Marathi example**     | **English mirror**                 |
|--------------------|-------------------------|------------------------------------|
| soil.shallow_black | उथळी काळी जमीन          | Shallow black soil                 |
| irrigation.none    | सिंचनाची सुविधा नाही      | No irrigation                      |
| risk.high          | जास्त धोका               | High risk                          |
| result.why         | हे का दाखवले आहे?          | Why am I seeing this?              |
| action.recalculate | परिस्थिती बदलून पुन्हा पाहा | Change assumptions and recalculate |

## UX principles

- Prefer short labels, cards, icons and comparative wording over dense paragraphs.

- Never rely on colour alone for Low/Medium/High risk; always include text labels.

- Use ranges and qualitative bands when the underlying data is uncertain.

- Always show “data as of” time for live/market information.

- Keep the primary flow completable in roughly two minutes for a supported location.

- Avoid jargon such as percentile, evapotranspiration or probability unless expanded in simple language.

# 10. Data Sources and Provider Strategy

The system shall isolate external data providers behind internal interfaces so that the prototype does not depend on one service. Provider outputs should be normalized into stable internal weather, climate and market schemas.

| **Data need**             | **V1 source**                                               | **Fallback / later**            | **Access note**                                                         | **Use in product**                                      |
|---------------------------|-------------------------------------------------------------|---------------------------------|-------------------------------------------------------------------------|---------------------------------------------------------|
| Forecast / recent weather | Open-Meteo                                                  | IMD official API                | Open-Meteo free non-commercial tier; IMD portal requires account/access | Rainfall/temperature context and scenario signals       |
| Historical climate        | NASA POWER + Open-Meteo historical                          | IMD historical datasets later   | NASA POWER daily meteorology available from 1981 to near real time      | Dry-spell and seasonal historical context               |
| Market prices             | data.gov.in / AGMARKNET                                     | Other mandi feeds later         | Daily mandi resource updated on OGD platform; API access supported      | Recent/seasonal price distribution and downside context |
| Agronomy rules            | ICAR-CRIDA contingency plan + university/PoCRA publications | KVK/agronomist validation later | Version as curated internal knowledge, not scraped live                 | Crop eligibility, sowing windows and contingency logic  |
| Soil                      | User-entered soil depth/class                               | GIS/soil data later             | No V1 dependency on field-level soil API                                | Major agronomic constraint and water-holding proxy      |

## Provider abstraction requirement

- WeatherProvider: get_forecast(location, date_range), get_recent_observations(location, date_range).

- ClimateProvider: get_historical_daily(location, years), derive_dry_spell_metrics(...).

- MarketProvider: get_prices(commodity, market/region, date_range).

- AgronomyRepository: get_crop_profiles(region, season), get_rules(rule_version).

# 11. Technical Architecture — V1 Direction

V1 should be implemented as a modular monolith, not a microservice system. This keeps deployment and iteration simple while preserving clear module boundaries that can be split later if scale, ownership or failure isolation justifies it.

```text
Marathi / English PWA
        |
        v
     FastAPI
        |
 +------+-----------------------------+
 |      |              |              |
Field  Decision       Data        Explainability
Module Engine        Adapters        / i18n
                      / | \
                Weather Market Climate
                   |      |      |
              Open-Meteo  OGD  NASA POWER
                       \  |  /
                PostgreSQL / PostGIS
                + cache + scheduled ingestion
```

## V1 modules

- Field Profile: validates location/soil/acreage/irrigation/sowing-date/budget inputs.

- Agronomy Rules: versioned crop profiles and contingency rules.

- Decision Engine: candidate filtering, scenario scoring and explanation generation.

- Data Adapters: external provider clients, normalization, retries and fallbacks.

- Time-Series Store: weather and market observations used for repeatable analysis/back-testing.

- i18n / Content: curated Marathi + English message catalogue.

- Provenance: source ID, rule version, observation timestamp and calculation timestamp.

- Observability: structured logs, provider latency/error metrics and failed-ingestion alerts.

# 12. Non-Functional Requirements

| **ID** | **Quality**     | **Requirement**                                                                                                                                       |
|--------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| NFR-01 | Explainability  | Every risk label must be traceable to input data and named rules.                                                                                     |
| NFR-02 | Reproducibility | Given the same stored inputs, rule version and data snapshot, the same result shall be reproducible.                                                  |
| NFR-03 | Resilience      | External provider failure shall degrade gracefully; stale/fallback data must be visibly marked.                                                       |
| NFR-04 | Performance     | Target p95 result generation under 3 seconds when required data is already cached; external refresh may run asynchronously before/after user request. |
| NFR-05 | Localization    | All user-facing strings shall use localization keys; no hard-coded English in the primary flow.                                                       |
| NFR-06 | Accessibility   | Risk state shall be conveyed by text and iconography, not colour only; usable on low-end mobile screens.                                              |
| NFR-07 | Auditability    | Store calculation inputs, output, rule version and data-source timestamps for historical replay.                                                      |
| NFR-08 | Privacy         | Avoid collecting identity, Aadhaar, financial account or sensitive personal data in V1.                                                               |
| NFR-09 | Security        | Validate/sanitize inputs, keep API secrets server-side and use HTTPS for deployed environments.                                                       |
| NFR-10 | Cost            | Prefer free/open/public data and low-cost hosting suitable for a personal prototype.                                                                  |

# 13. V1 Acceptance Criteria

- A supported Dharashiv location can be selected and the field form can be completed in Marathi.

- At least three curated Kharif crop/cropping-system options can be produced for a representative field scenario.

- Changing soil depth, irrigation availability or sowing date can change candidate eligibility or risk in a traceable way.

- At least one weather provider and one historical-climate provider are integrated through internal provider interfaces.

- Market-price data for supported commodities can be ingested and summarized into a documented risk metric.

- Each candidate displays agronomic fit, climate risk, approximate financial exposure, price context and a plain-language explanation.

- Every result displays the data freshness and rule/source version used to calculate it.

- The system can replay at least one historical Kharif scenario (target: 2023 Dharashiv dry-spell case) using stored/historical data.

- English and Marathi renderings convey the same underlying decision state.

- The README and UI clearly state that V1 is an educational/research prototype and not field-validated agricultural advice.

# 14. Prototype Success Metrics

Because there is no farmer pilot in V1, success metrics should measure product correctness and learning rather than yield or income impact.

| **Metric**                | **V1 target**                                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------------------------------|
| Decision traceability     | 100% of displayed risk labels resolve to rule IDs and input/source data.                                          |
| Data freshness visibility | 100% of weather/market result cards expose source and timestamp.                                                  |
| Localization completeness | 100% of primary-flow strings available in Marathi and English.                                                    |
| Historical replay         | At least one documented difficult Kharif season can be replayed end-to-end.                                       |
| Scenario sensitivity      | At least three input changes produce explainable, testable changes in output.                                     |
| Provider resilience       | Simulated weather-provider failure yields a visible fallback/stale state rather than a silent error.              |
| Portfolio quality         | Architecture, trade-offs and evolution path can be explained clearly in a 10–15 minute system-design walkthrough. |

# 15. Validation Plan and Delivery Stages

| **Stage**                                | **Work**                                                                                         | **Exit criterion**                                                 |
|------------------------------------------|--------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| Stage 0 — PRD / assumptions              | Freeze product boundary, assumptions and evidence sources.                                       | This document.                                                     |
| Stage 1 — Dharashiv deep dive            | Build crop × soil × sowing window × irrigation × climate × cost × price × contingency matrix.    | Versioned agronomy/risk matrix with citations.                     |
| Stage 2 — Manual worked case             | Run one representative farm scenario by hand and produce Marathi risk cards.                     | If output is not explainable/sensible, revise rules before coding. |
| Stage 3 — Data spike                     | Integrate Open-Meteo, NASA POWER and AGMARKNET/OGD; validate response quality and storage model. | Repeatable normalized data pipeline.                               |
| Stage 4 — Software MVP                   | Implement field form, decision engine, risk cards, what-if and provenance.                       | Deployed personal prototype.                                       |
| Stage 5 — Historical replay              | Replay 2023-style delayed/erratic rainfall scenario and other selected seasons.                  | Documented case studies and decision traces.                       |
| Stage 6 — Optional real-world validation | Later: interview farmers/KVK/agronomists and compare advice with field practice.                 | Required before any real farmer-facing claim.                      |

# 16. Risks, Constraints and Mitigations

| **Risk**                     | **Why it matters**                                                          | **Mitigation**                                                                                             |
|------------------------------|-----------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| Agronomic correctness        | A software team can misread domain guidance.                                | Keep rules explicit, source-linked and versioned; seek agronomist/KVK review before real-world use.        |
| False precision              | Yield/price/risk numbers may appear more certain than they are.             | Use ranges/bands, expose assumptions and avoid fabricated probabilities.                                   |
| Weather-provider mismatch    | Global-model forecast may differ from local IMD guidance.                   | Provider abstraction; prefer official IMD when access is available; disclose source.                       |
| Sparse mandi data            | A local crop/market combination may have missing or irregular observations. | Use quality checks, regional fallback only when clearly labelled, and suppress weak price conclusions.     |
| Historical ≠ future          | Climate distribution is changing.                                           | Use historical data as context, not a deterministic forecast; include current/seasonal signals separately. |
| Marathi terminology quality  | Literal translation may be unnatural or misleading.                         | Curate terms manually and later validate wording with Maharashtra users/agronomists.                       |
| Project scope creep          | Agri-tech naturally expands into pest, insurance, inputs, credit, etc.      | Use the V1 non-goals as a hard boundary.                                                                   |
| Free API limits/availability | Prototype services may change limits or uptime.                             | Cache data, monitor providers and keep adapters replaceable.                                               |

# 17. Open Questions for the Dharashiv Deep Dive

- Which exact 3–5 crop/cropping-system options should V1 support, and under which soil/sowing-window combinations?

- What input-cost ranges per acre are defensible and recent enough for each supported option?

- Which Dharashiv/taluka markets should be used for price history, and what is the fallback hierarchy when a commodity is missing?

- How should “one protective irrigation” change crop risk quantitatively/qualitatively?

- Which rainfall thresholds define a dry-spell scenario for each crop stage, and which are generic versus crop-specific?

- How should excess-rain/waterlogging risk be represented for shallow/medium/deep black soils?

- What time horizon of market-price history is useful for V1 — 3 years, 5 years, or seasonally weighted?

- Should budget be an exact rupee amount or simple Low / Medium / Flexible bands in the primary UX?

- Which terms in Marathi should use farmer-common vocabulary rather than formal agricultural terminology?

- What evidence is required before changing the UI wording from “risk comparison” to any stronger recommendation language?

# 18. Deliberate Post-V1 Evolution (Not Commitments)

- Official IMD provider as primary source once API access is available and terms fit the project.

- Geospatial soil suggestion with farmer confirmation rather than automatic truth.

- Seasonal forecast and probabilistic scenario calibration.

- Voice/audio Marathi output for lower-literacy use cases.

- Additional Maharashtra districts using separate agronomy rule packs.

- Farmer/KVK co-design and field validation.

- Only after sufficient validated observations: statistical/ML calibration of component risk — while preserving explainability.

# 19. Initial Evidence and Data References

**1. PoCRA Concurrent Monitoring Round X Report (2024) —** Dharashiv/Latur soil distribution, rainfall distribution and Kharif 2023 dry-spell observations. [<u>Source</u>](https://mahapocra.gov.in/assets/docs/mne/Final_Report_SambodhiCM_PoCRA_1June2024.pdf)

**2. ICAR-CRIDA District Agriculture Contingency Plan — Osmanabad/Dharashiv —** Soil/crop contingency logic for delayed rainfall, crop establishment failure and mid-season drought. [<u>Source</u>](https://www.icar-crida.res.in/CP-2012/statewiseplans/Maharastra%28Pdf%29/MAU%2C%20Parbhani/Maharashtra%2030-Osmanabad-%2031-12-2011.pdf)

**3. IMD API Management Platform —** Official weather observations, forecasts, warnings and specialized bulletins; account/access required for API usage. [<u>Source</u>](https://api.imd.gov.in/public/index.php)

**4. Open-Meteo API / Terms —** No-key free API for non-commercial use within documented rate limits; forecast and historical weather. [<u>Source</u>](https://open-meteo.com/en/terms)

**5. NASA POWER Daily API —** Daily analysis-ready meteorological data; daily data available from 1981 to near real time. [<u>Source</u>](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)

**6. Open Government Data — Daily Mandi Prices —** AGMARKNET/DMI daily commodity-market price resource, exposed through the OGD platform. [<u>Source</u>](https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi)

# 20. Version History

| **Version** | **Date**    | **Status** | **Change**                                                                                                    |
|-------------|-------------|------------|---------------------------------------------------------------------------------------------------------------|
| 0.1         | 26 Sep 2026 | Draft      | Initial PRD based on agreed Dharashiv, Kharif, Marathi-first climate + financial risk decision-support scope. |
