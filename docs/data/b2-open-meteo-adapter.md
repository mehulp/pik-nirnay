# Pik Nirnay — B2 Open-Meteo Weather Adapter

**Project:** Pik Nirnay / पीक निर्णय  
**Workstream:** B2 — Open-Meteo Weather Adapter  
**Version:** V0.2 — reviewed  
**Status:** READY TO FREEZE FOR V1  
**Scope:** Concrete Open-Meteo implementation of the frozen B1 WeatherProvider contract  
**Depends on:** B1 V0.2 frozen/implemented  
**Does not include:** geocoding, B3 historical/reanalysis provider, agronomic derivation

---

## 1. Review conclusion

B2 V0.1 had the correct core design:

```text
B1 WeatherWindowRequest
        ↓
Open-Meteo /v1/forecast
        ↓
provider-specific validation/normalization
        ↓
B1 WeatherWindowResult
```

The review keeps the main architecture but makes these refinements:

1. Clarifies that the free Open-Meteo API is **non-commercial only**, with current call limits and no uptime guarantee.
2. Makes attribution an explicit product requirement for any future weather display.
3. Keeps `/v1/forecast`, best-match model selection, exact start/end dates, and `cell_selection=land`.
4. Keeps archived/live basis classification separate from B1 temporal position.
5. Avoids overclaiming exact-date range behaviour that is not stated as clearly as `past_days`/`forecast_days`.
6. Refines 401/403 error handling because B2 V1 has no authentication.
7. Adds verification of India UTC offset when Open-Meteo returns it.
8. Preserves the principle that recent past forecast data are archived/model forecasts, not physical observations.

---

## 2. Selected Open-Meteo product

Use:

```text
https://api.open-meteo.com/v1/forecast
```

Use the generic Weather Forecast API with default/best-match model selection.

Do not pin a specific meteorological model in V1.

Why:

- Open-Meteo's generic API automatically selects/combines suitable forecast models.
- the generic API is the recommended worldwide entry point,
- Pik Nirnay does not currently compare meteorological models,
- best-match may involve more than one underlying model, so provenance must not invent a single model name.

Do not use in B2:

```text
Historical Weather API
Historical Forecast API
Single Runs API
Previous Runs API
Climate API
```

Those belong to B3/future replay work.

---

## 3. Current documented provider capability

Open-Meteo's current generic Forecast API documents:

```text
past_days: 0–92
forecast_days: 0–16
```

and exact:

```text
start_date
end_date
```

parameters.

B2 capability declaration:

```text
provider_id = "open_meteo"

supported_variables = {
    DAILY_PRECIPITATION,
    DAILY_TEMPERATURE_MIN,
    DAILY_TEMPERATURE_MAX,
    DAILY_ET0
}

supports_past = true
supports_current_day = true
supports_future = true

max_past_days = 92
max_future_days = 16
```

These values describe the provider integration and may change independently of B1.

### Exact-date range caution

The provider documentation clearly publishes `past_days=0–92` and `forecast_days=0–16`.

It also supports exact `start_date` / `end_date`, but the exact rolling-bound semantics for every exact-date combination are less explicitly documented.

Therefore:

- use B1 capability validation where it is unambiguous,
- reject obviously unsupported rolling ranges when safely derivable,
- do **not** build fragile off-by-one behaviour from guesswork,
- if an exact-date boundary remains ambiguous, allow Open-Meteo to reject it and normalize the provider error.

Do not make an external HTTP call solely to discover this at runtime if the request is obviously impossible.

---

## 4. Free / commercial access — V1 policy

For the current research/portfolio prototype, use Open-Meteo's free/open-access endpoint:

```text
https://api.open-meteo.com
```

Current free-tier conditions:

```text
non-commercial use only
no API key / no sign-up required
up to 600 calls/minute
up to 5,000 calls/hour
up to 10,000 calls/day
up to 300,000 calls/month
no uptime guarantee
```

B2 does not implement quota tracking or rate limiting.

### Commercial use

If Pik Nirnay later becomes commercial—for example:

- paid product,
- subscription app,
- advertising-supported product,
- integration into a commercial product—

the free endpoint must no longer be assumed appropriate.

Commercial use requires reviewing/subscribing to Open-Meteo's customer API plans.

The customer endpoint currently uses:

```text
customer-api.open-meteo.com
```

with an API key.

Do not implement this in B2 V1.

---

## 5. Attribution requirement

Open-Meteo API data are provided under CC BY 4.0-style attribution requirements.

Record this as an explicit future UI requirement:

```text
B2-REQ-ATTRIBUTION
Whenever Open-Meteo weather data are displayed to the user,
show clear Open-Meteo attribution with the required link.
```

Example wording from Open-Meteo's licence guidance:

```text
Weather data by Open-Meteo.com
```

B2 itself should not add a UI-specific field to B1.

Keep:

```text
provider_id = "open_meteo"
```

in provenance so the presentation layer knows the source.

---

## 6. B1 → Open-Meteo variable mapping

```text
DAILY_PRECIPITATION
    -> daily=precipitation_sum

DAILY_TEMPERATURE_MIN
    -> daily=temperature_2m_min

DAILY_TEMPERATURE_MAX
    -> daily=temperature_2m_max

DAILY_ET0
    -> daily=et0_fao_evapotranspiration
```

Request only variables requested by B1.

Do not request extra fields simply because the provider exposes them.

---

## 7. Request mapping

```text
B1 latitude  -> latitude
B1 longitude -> longitude

start_date -> start_date
end_date   -> end_date
```

Use exact B1 date ranges.

Do not convert the request to `past_days` / `forecast_days` unless a future reviewed implementation reason requires it.

---

## 8. Fixed provider parameters

Send explicitly:

```text
timezone=Asia/Kolkata
temperature_unit=celsius
precipitation_unit=mm
timeformat=iso8601
cell_selection=land
```

Explicit parameters make the adapter deterministic and self-documenting.

---

## 9. Cell-selection policy

Use:

```text
cell_selection=land
```

for V1.

This matches Open-Meteo's documented/default terrain-optimised behaviour:

- prefer land,
- select a suitable grid cell,
- account for elevation using the provider's DEM.

This is an integration decision, not an agronomic claim.

Preserve provider-returned coordinates/elevation in provenance.

Do not expose `cell_selection` in B1.

---

## 10. Model-selection policy

Do not send a specific `models=` value.

Use generic/default best-match behaviour.

Recommended B1 provenance:

```text
provider_id = "open_meteo"
provider_dataset = "weather_forecast_api"

provider_model = None
provider_run_id = None
provider_run_initialized_at = None
```

unless future provider responses explicitly establish reliable values.

Do not infer a single model name from provider documentation.

---

## 11. Temporal position vs data basis

These answer different questions.

### TemporalPosition

Owned by B1:

```text
relative to request.reference_date
```

### WeatherDataBasis

Owned by B2:

```text
how Open-Meteo produced/served that record
```

Do not use B1 `reference_date` to classify provider basis.

---

## 12. Data-basis classification

Open-Meteo's Forecast API documents Past Days as access to archived forecasts.

For records returned through the live Forecast API:

```text
record.date < provider_local_retrieval_date
    -> ARCHIVED_FORECAST

record.date >= provider_local_retrieval_date
    -> LIVE_FORECAST
```

Use the actual retrieval instant converted to `Asia/Kolkata`.

This allows valid combinations such as:

```text
TemporalPosition.FUTURE
WeatherDataBasis.ARCHIVED_FORECAST
```

when evaluating a historical B1 reference date using data fetched today.

### Limitation

`ARCHIVED_FORECAST` here means provider-served archived forecast/model output.

It does **not** mean:

- station observation,
- reanalysis,
- or exact forecast information known to a farmer at a historical decision instant.

Historical decision-time replay remains B3.

---

## 13. Injectable clock

Use one injectable clock:

```python
clock() -> timezone-aware UTC datetime
```

Capture it once per provider request.

Use that same instant for:

```text
WeatherProvenance.retrieved_at
provider-local retrieval date
data-basis classification
```

Do not call the wall clock separately for every record.

---

## 14. HTTP client

Use the repository's existing async HTTP convention.

If no wrapper already exists, an injectable `httpx.AsyncClient` is acceptable if `httpx` is already part of the project.

Requirements:

- no new client per record,
- mockable/injectable transport,
- automated tests require no Internet,
- do not add another HTTP library unnecessarily.

---

## 15. Timeout

Recommended default:

```text
10 seconds
```

Keep configurable.

No infinite/unbounded request waits.

---

## 16. Retries

B2 V1 performs:

```text
0 automatic retries
```

Normalized errors may still be marked retryable.

Retry/backoff policy belongs above B2.

---

## 17. Capability/range validation

Before network I/O:

```text
validate_request_against_capabilities(...)
```

Use provider-local current date rather than B1 `reference_date` for any rolling-range check.

Do not assume B1 reference date equals today's date.

For exact-date edge cases where published docs do not establish an unambiguous boundary, prefer:

```text
provider validation
→ normalized B1 error
```

over hidden guessed rules.

---

## 18. Response fields used

Provider-specific B2 parsing may use:

```text
latitude
longitude
elevation
timezone
utc_offset_seconds
daily
daily_units
```

Fields such as:

```text
generationtime_ms
timezone_abbreviation
```

do not need to enter B1.

---

## 19. Resolved location

Map Open-Meteo returned:

```text
latitude
longitude
```

to:

```text
WeatherProvenance.resolved_point
```

and returned:

```text
elevation
```

to:

```text
WeatherProvenance.resolved_elevation_m
```

Do not overwrite the original B1 requested point.

---

## 20. Timezone validation

B2 explicitly requests:

```text
Asia/Kolkata
```

Verify provider response timezone is compatible.

Expected:

```text
timezone = Asia/Kolkata
```

When provided, also verify:

```text
utc_offset_seconds = 19800
```

for India Standard Time.

If response timezone/offset is incompatible:

```text
MALFORMED_RESPONSE
```

Do not silently reinterpret daily values.

---

## 21. Unit validation

Expected daily units:

```text
precipitation_sum = mm

temperature_2m_min = °C
temperature_2m_max = °C

et0_fao_evapotranspiration = mm
```

Verify requested variables' returned units.

If incompatible:

```text
MALFORMED_RESPONSE
```

Do not silently perform surprise unit conversion.

---

## 22. Daily array normalization

Open-Meteo returns parallel arrays.

Require:

```text
len(daily.time)
==
len(each explicitly requested daily field)
```

If not:

```text
MALFORMED_RESPONSE
```

For each index:

```text
daily.time[i]
+
requested values[i]
    ↓
DailyWeatherRecord
```

Provider null values map to:

```text
None
```

Never map null precipitation to zero.

---

## 23. Missing requested field

If B2 requested a variable but the entire response field is missing:

```text
MALFORMED_RESPONSE
```

If the field exists but one daily entry is null:

```text
None
```

and B1 completeness/coverage logic handles it.

---

## 24. Missing calendar date

If the response is structurally valid but a requested date is omitted:

- do not interpolate,
- do not synthesize a zero value,
- construct records only for returned dates.

B1 derives:

```text
dates_missing_required_data
required_data_coverage
```

---

## 25. Duplicate dates

Duplicate normalized local dates:

```text
MALFORMED_RESPONSE
```

Do not merge them.

---

## 26. Ordering

Do not silently conceal malformed provider ordering.

Follow frozen B1 result behaviour.

If B1 requires ascending input and Open-Meteo returns invalid ordering:

```text
MALFORMED_RESPONSE
```

rather than silently repairing ambiguous provider data.

---

## 27. Let B1 derive cross-object state

B2 should not duplicate logic for:

```text
TemporalPosition
RecordCompleteness
RequiredDataCoverage
dates_missing_required_data
```

Construct normalized values and let the frozen B1 result model perform its authoritative derivation/validation.

B2 only supplies the provider-specific `WeatherDataBasis`.

---

## 28. Error mapping

Recommended:

```text
transport timeout
    -> TIMEOUT
       retryable=true

DNS / connection failure
    -> PROVIDER_UNAVAILABLE
       retryable=true

HTTP 429
    -> RATE_LIMITED
       retryable=true

HTTP 5xx
    -> PROVIDER_UNAVAILABLE
       retryable=true

HTTP 400
    -> INVALID_REQUEST
       retryable=false

HTTP 401
    -> AUTHENTICATION_FAILED
       retryable=false

HTTP 403
    -> UNKNOWN_PROVIDER_ERROR
       retryable=false
       unless the response clearly establishes an authentication issue

invalid/non-JSON 2xx response
    -> MALFORMED_RESPONSE
       retryable=false

schema/array/unit/timezone mismatch
    -> MALFORMED_RESPONSE
       retryable=false

other unexpected status
    -> UNKNOWN_PROVIDER_ERROR
```

### Why 403 changed

The free V1 endpoint requires no authentication.

A 403 should therefore not automatically be described as an authentication failure.

It may represent access blocking, service policy, or another provider condition.

---

## 29. Provider JSON errors

Open-Meteo uses HTTP 400 JSON errors such as:

```json
{
  "error": true,
  "reason": "..."
}
```

Retain provider `reason` only for internal diagnostics.

Do not expose it as B1 `safe_message`.

Avoid broad/fragile substring classification.

A narrowly tested provider-range error may later map to `UNSUPPORTED_RANGE` if useful.

---

## 30. DATA_UNAVAILABLE

Do not use `DATA_UNAVAILABLE` because an otherwise valid response has:

```text
null precipitation
missing requested date
PARTIAL coverage
EMPTY coverage
```

These are valid B1 result states.

Use `DATA_UNAVAILABLE` only when the provider cannot supply a usable product/result at all and a normalized B1 result cannot be constructed.

---

## 31. Free-tier quotas

Current free/open-access operational limits:

```text
600 calls / minute
5,000 calls / hour
10,000 calls / day
300,000 calls / month
```

Do not encode these in `WeatherProviderCapabilities`.

They are account/service quotas rather than weather-data capabilities.

Do not implement rate limiting in B2 V1.

---

## 32. Provider configuration

Recommended:

```text
base_url
timeout_seconds
```

Defaults:

```text
base_url = "https://api.open-meteo.com/v1/forecast"
timeout_seconds = 10
```

Do not add commercial API configuration in B2 V1.

---

## 33. Logging/privacy

Do not log precise requested farm coordinates at INFO level.

Safe operational metadata:

```text
provider_id
request date range
returned record count
coverage status
normalized error code
elapsed duration
```

Do not log raw provider JSON by default.

---

## 34. Testing strategy

All normal automated tests use mocked/injected HTTP transport.

### Request mapping

Test:

- latitude/longitude,
- exact dates,
- `timezone=Asia/Kolkata`,
- metric units,
- `timeformat=iso8601`,
- `cell_selection=land`,
- correct daily variables,
- no extra B1-excluded fields.

### Capabilities

Test:

- four B1 variables,
- 92 past days,
- 16 forecast days,
- provider-local current date used rather than B1 reference date where relevant.

Do not write brittle off-by-one tests unless the exact-date behaviour is documented/confirmed.

### Response normalization

Test:

- precipitation,
- temperatures,
- ET₀,
- null values,
- omitted dates,
- resolved point/elevation,
- timezone,
- UTC offset,
- units.

### Data basis

With fixed clock:

- previous provider-local date -> ARCHIVED_FORECAST,
- current date -> LIVE_FORECAST,
- future date -> LIVE_FORECAST,
- classification independent from B1 reference date.

### Malformed responses

Test:

- invalid JSON,
- missing `daily`,
- missing `daily.time`,
- requested field absent,
- mismatched array lengths,
- duplicate dates,
- invalid ordering if applicable,
- incompatible timezone,
- incorrect IST offset,
- incompatible units.

### Errors

Test:

- timeout,
- network failure,
- 400,
- 401,
- 403,
- 429,
- 5xx,
- unexpected status.

### Non-goals

Verify no:

- geocoder,
- B3 provider,
- reanalysis,
- retries,
- cache/persistence,
- monsoon/sowing derivation,
- crop logic.

---

## 35. Optional live smoke test

A manual single-request smoke test may be used during development.

It must not:

- run in default pytest,
- be required for CI,
- consume significant quota,
- become a correctness dependency.

Live provider data are nondeterministic.

---

## 36. Suggested module structure

```text
data_adapters/
    weather/
        models.py
        contract.py
        errors.py

        providers/
            __init__.py
            open_meteo.py
```

Private parsing models/helpers are allowed.

Do not leak provider schemas into B1.

---

## 37. Explicit non-goals

B2 does not implement:

```text
geocoding
taluka/village -> coordinate resolution

Historical Weather
Historical Forecast
Previous Runs
Single Runs
Climate API

model comparison
soil moisture

monsoon onset/delay
sowing readiness
dry-spell/waterlogging logic

crop selection
risk scoring
financial scoring

automatic retry
provider fallback
Redis/cache/database persistence
```

---

## 38. Review decisions

| Question | Frozen V1 decision |
|---|---|
| Endpoint | **Generic `/v1/forecast`** |
| Model selection | **Default/best-match; no model pinning** |
| Date mapping | **Exact `start_date` / `end_date`** |
| Cell selection | **Explicit `land`** |
| Timezone | **Asia/Kolkata** |
| Units | **Explicit metric units** |
| Past data basis | **Archived forecast, not observation** |
| Current/future basis | **Live forecast** |
| Data-basis reference clock | **Actual retrieval-local date** |
| Automatic retries | **None** |
| Null/missing daily data | **Valid partial/empty B1 result where structurally valid** |
| Live API tests in CI | **No** |
| Commercial API support | **No in V1** |
| Free endpoint allowed use | **Non-commercial prototype only** |
| Attribution | **Mandatory when weather data are displayed** |
| 403 error | **Do not automatically call it authentication failure** |
| Exact rolling off-by-one | **Do not guess beyond documented behaviour** |

---

## 39. Open gaps / limitations

```text
B1-GAP-001
LocationContext -> trustworthy GeoPoint

B3-GAP-001
Historical replay:
realised weather vs decision-time forecast

B2-LIMIT-001
Best-match may combine/select multiple weather models.
One stable model/run identity is not guaranteed.

B2-LIMIT-002
The free Open-Meteo endpoint is non-commercial and has no uptime guarantee.

B2-REQ-ATTRIBUTION
Future UI must display required Open-Meteo attribution wherever its weather data are shown.
```

---

## 40. Freeze decision

**Status: `READY_TO_FREEZE` for the V1 prototype.**

B2 now defines a deliberately thin adapter:

```text
Open-Meteo-specific HTTP + schema
        ↓
strict validation
        ↓
B1-normalized weather result
```

without importing provider assumptions into crop/agronomic logic.
