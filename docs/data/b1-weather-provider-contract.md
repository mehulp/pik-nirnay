# Pik Nirnay — B1 WeatherProvider Contract

**Project:** Pik Nirnay / पीक निर्णय  
**Workstream:** B1 — WeatherProvider Contract  
**Version:** V0.2 — reviewed  
**Status:** READY TO FREEZE FOR V1  
**Scope:** Provider-neutral near-current daily weather contract for Dharashiv Kharif V1  
**Depends on:** C1 V0.2, C2 V0.2, C3 V0.2  
**Next:** B2 Open-Meteo adapter; B3 historical-weather/replay design

---

## 1. Review conclusion

B1 V0.1 had the correct architectural boundary:

```text
external weather provider
        ↓
provider adapter
        ↓
normalized weather facts
        ↓
future reviewed agronomic derivation
        ↓
C1 SeasonContext
```

The review makes these important corrections:

1. Remove `elevation_m` from the caller-supplied V1 `GeoPoint`; provider-resolved elevation may be preserved in provenance instead.
2. Remove duplicate requested-location/timezone data from provenance; the request already owns those values.
3. Refine data-basis semantics so "recent past" is not confused with physical observation.
4. Remove `REANALYSIS` from the active B1 basis vocabulary; B3 owns historical/reanalysis semantics.
5. Clarify missing-date vs missing-required-value behaviour.
6. Add `UNSUPPORTED_VARIABLE` as a normalized provider error.
7. Make requested variables unique/immutable.
8. Clarify that provenance improves auditability but does not guarantee exact forecast replay unless responses/run identifiers are persisted.
9. Explicitly flag that B3 must distinguish historical realised weather/reanalysis from historical forecasts available at decision time.

---

# 2. Purpose

B1 defines what Pik Nirnay is allowed to ask of a near-current weather provider and what normalized weather facts the adapter may return.

B1 does not determine:

- monsoon onset,
- monsoon delay,
- sowing-moisture readiness,
- dry-spell state,
- waterlogging state,
- crop suitability,
- crop recommendation.

Those require separately reviewed domain logic.

---

# 3. Core boundary

```text
External provider API
        ↓
B2 adapter
        ↓
B1 normalized weather result
        ↓
future reviewed derivation service
        ↓
C1 SeasonContext
        ↓
C3 / future decision engine
```

Provider-specific fields must never appear directly in agronomic rules.

---

# 4. B1 versus B3

## B1 WeatherProvider

Purpose:

```text
near-current decision support
```

Typical data:

- recent archived/model weather,
- current-day forecast/model data,
- short-range forecast.

## B3 historical/replay layer

Purpose:

- historical realised-weather context,
- historical reanalysis,
- historical-season reconstruction,
- decision-time replay where appropriate.

### Important B3 gap discovered during review

Historical replay has two different meanings:

```text
A. What weather actually happened?
    -> observations/reanalysis

B. What forecast information was available on that historical decision date?
    -> historical forecast archive / model run
```

These must not be silently treated as equivalent.

Open-Meteo exposes separate Historical Weather and Historical Forecast products, which reinforces the need to make this distinction explicitly in B3.

**Gap:** `B3-GAP-001 — define replay semantics: realised weather vs information available at decision time.`

B1 does not solve this gap.

---

# 5. V1 weather variables

## 5.1 Mandatory

```text
WeatherVariable.DAILY_PRECIPITATION
```

Normalized unit:

```text
mm per local calendar day
```

This is the only mandatory V1 metric.

---

## 5.2 Optional

```text
DAILY_TEMPERATURE_MIN
DAILY_TEMPERATURE_MAX
DAILY_ET0
```

Units:

```text
temperature -> °C
ET₀         -> mm/day
```

These are supported by the contract but currently have no agronomic decision semantics.

---

## 5.3 Deliberately excluded

Do not include in B1 V1:

```text
soil moisture
soil temperature
precipitation probability
humidity
wind
weather code
cloud cover
solar radiation
```

They may be added only after a reviewed product/domain need appears.

Provider soil moisture must never be used as a shortcut for:

```text
SowingMoistureStatus.READY
```

---

# 6. GeoPoint

V1 request coordinates:

```text
GeoPoint
    latitude
    longitude
```

Validation:

```text
-90 <= latitude <= 90
-180 <= longitude <= 180
```

Coordinate reference:

```text
WGS84
```

## Why `elevation_m` was removed from the request model

Open-Meteo and similar gridded providers may use their own digital-elevation/grid-selection logic.

Allowing an arbitrary caller-supplied elevation in V1 would create another unreviewed input capable of changing provider output.

If provider-resolved elevation is returned, preserve it as provenance.

A reviewed future requirement may add caller-supplied field elevation later.

---

# 7. Coordinate provenance

```text
CoordinateSource
    FIELD_COORDINATE
    VILLAGE_CENTROID
    TALUKA_CENTROID
    GEOCODED
    TEST_FIXTURE
    UNKNOWN
```

```text
WeatherLocation
    point
    coordinate_source
    location_label?
```

`location_label` is diagnostic/display metadata only.

No weather or crop rule may depend on it.

---

# 8. Location-resolution gap

C1 stores:

```text
district
taluka
village_name?
```

but not coordinates.

B1 does not define how those values become a `GeoPoint`.

Never silently use a centroid while claiming field-level precision.

When a centroid is used, its source must be explicit.

**Gap:** `B1-GAP-001 — reviewed location-to-coordinate resolution strategy.`

---

# 9. WeatherWindowRequest

```text
WeatherWindowRequest
    location
    start_date
    end_date
    reference_date
    timezone
    requested_variables
```

---

## 9.1 Date range

```text
start_date <= end_date
```

Both dates are inclusive.

Do not encode provider-specific date-range limits in B1.

Adapters expose such limitations through capabilities/errors.

---

## 9.2 `reference_date`

Renamed from `as_of_date` for clarity.

Meaning:

> The local calendar date relative to which returned records are classified as past, current-day, or forecast.

This should normally correspond to the caller's assessment date.

Do not use the machine's current date implicitly.

No validation against `date.today()` belongs in B1.

---

## 9.3 Timezone

For Dharashiv V1:

```text
Asia/Kolkata
```

This should be a pinned/validated value rather than an unrestricted timezone string.

Daily values mean local calendar-day aggregates in this timezone.

---

## 9.4 Requested variables

Use an immutable unique collection such as:

```text
frozenset[WeatherVariable]
```

or the equivalent project convention.

Requirements:

```text
DAILY_PRECIPITATION must be present
duplicates cannot occur
```

An adapter must reject a requested optional variable it does not support.

---

# 10. TemporalPosition

Rename `WeatherDayRole` to:

```text
TemporalPosition
    PAST
    CURRENT_DAY
    FUTURE
```

Classification:

```text
date < reference_date  -> PAST
date == reference_date -> CURRENT_DAY
date > reference_date  -> FUTURE
```

This is purely a date relationship.

It does not describe how the weather value was produced.

This avoids terms such as `FORECAST` being overloaded between time position and data provenance.

---

# 11. WeatherDataBasis

For B1:

```text
WeatherDataBasis
    OBSERVATION
    MODEL_ESTIMATE
    LIVE_FORECAST
    ARCHIVED_FORECAST
    UNKNOWN
```

### OBSERVATION

Provider explicitly supplies observed/station-style data.

### MODEL_ESTIMATE

Provider supplies model-derived near-current data that is not accurately described as a forecast or direct observation.

### LIVE_FORECAST

Forecast data from a current model run/service.

### ARCHIVED_FORECAST

Past-valid-time data drawn from archived forecast output.

### UNKNOWN

Provider semantics cannot be established confidently.

## Why `REANALYSIS` is excluded

Reanalysis belongs to B3 historical-weather semantics.

If B3 reuses common weather value objects later, shared types can be extracted deliberately rather than making the B1 contract broader than its purpose.

---

# 12. DailyWeatherRecord

```text
DailyWeatherRecord
    date
    temporal_position
    data_basis

    precipitation_mm

    temperature_min_c?
    temperature_max_c?
    et0_mm?

    completeness
```

---

## 12.1 Precipitation

```text
precipitation_mm: float | None
```

When present:

```text
precipitation_mm >= 0
```

Missing:

```text
None
```

Never:

```text
missing -> 0
```

---

## 12.2 Temperature

Optional:

```text
temperature_min_c
temperature_max_c
```

If both exist:

```text
temperature_min_c <= temperature_max_c
```

No crop thresholds belong here.

---

## 12.3 ET₀

Optional:

```text
et0_mm >= 0
```

ET₀ is retained only as normalized weather data.

Do not turn it into crop-stress or irrigation advice.

---

# 13. RecordCompleteness

```text
RecordCompleteness
    COMPLETE
    PARTIAL
    MISSING
```

Relative to the request's variables:

### COMPLETE
All requested variables are present.

### PARTIAL
The mandatory precipitation value is present, but one or more requested optional values are absent; or some requested values exist while others do not.

### MISSING
No requested weather value for that represented date is usable.

This describes field completeness, not meteorological accuracy.

---

# 14. Required-data coverage

Rename response coverage semantics conceptually to:

```text
RequiredDataCoverage
    COMPLETE
    PARTIAL
    EMPTY
```

Coverage is based on the mandatory V1 value:

```text
DAILY_PRECIPITATION
```

### COMPLETE

Every requested date has usable precipitation.

### PARTIAL

At least one requested date lacks usable precipitation, while at least one requested date has it.

### EMPTY

No requested date has usable precipitation.

This is intentionally different from `RecordCompleteness`.

A request can therefore have:

```text
RequiredDataCoverage.COMPLETE
```

while individual records are:

```text
RecordCompleteness.PARTIAL
```

because an optional temperature/ET₀ value is missing.

---

# 15. Missing required-data dates

Use:

```text
dates_missing_required_data[]
```

rather than the ambiguous name `missing_dates`.

This list contains any requested local date for which usable mandatory precipitation is unavailable, whether:

- the provider omitted the date entirely, or
- the provider returned the date but precipitation was missing/null.

Adapters must not interpolate such dates.

---

# 16. WeatherWindowResult

```text
WeatherWindowResult
    request
    records
    required_data_coverage
    dates_missing_required_data
    provenance
```

Invariants:

- records are ascending by date,
- at most one record exists per local date,
- every record date falls inside the request range,
- duplicate normalized dates are rejected before result creation,
- coverage fields agree with records/request dates.

Provider adapters own any provider-specific duplicate-resolution behaviour before constructing this model.

---

# 17. WeatherProvenance

Avoid duplicating request-owned data.

Recommended:

```text
WeatherProvenance
    provider_id
    provider_dataset?
    provider_model?
    provider_run_id?
    provider_run_initialized_at?
    retrieved_at
    resolved_point?
    resolved_elevation_m?
```

Do NOT repeat:

```text
requested_location
requested_timezone
```

because these already live in `WeatherWindowResult.request`.

---

## 17.1 Provider identification

```text
provider_id
```

Stable adapter ID, e.g.:

```text
open_meteo
```

Optional:

```text
provider_dataset
provider_model
provider_run_id
provider_run_initialized_at
```

Populate only when the provider actually exposes/supports the information.

Never invent model/run metadata.

---

## 17.2 Retrieval time

```text
retrieved_at
```

Must be timezone-aware UTC.

---

## 17.3 Resolved grid point

Gridded providers may resolve to a cell a few kilometres away from the requested point.

When exposed by the provider, preserve:

```text
resolved_point
resolved_elevation_m
```

The caller can compare these with:

```text
result.request.location.point
```

without duplicating the requested coordinate in provenance.

---

# 18. Provenance does not equal exact replay

`retrieved_at` + provider/model metadata improves:

- auditability,
- debugging,
- change analysis.

It does **not** automatically guarantee that the exact live forecast can be reconstructed later.

Exact forecast replay may require:

- response snapshot persistence,
- provider run identifiers,
- or a historical/single-run forecast archive.

B1 does not promise exact replay.

This must remain explicit.

---

# 19. Provider capabilities

```text
WeatherProviderCapabilities
    provider_id
    supported_variables
    supports_past
    supports_current_day
    supports_future
    max_past_days?
    max_future_days?
```

Use immutable unique sets for `supported_variables`.

These are integration capabilities, not agronomic facts.

---

# 20. WeatherProvider interface

Conceptual:

```python
class WeatherProvider(Protocol):
    @property
    def provider_id(self) -> str:
        ...

    def capabilities(self) -> WeatherProviderCapabilities:
        ...

    async def get_daily_weather(
        self,
        request: WeatherWindowRequest,
    ) -> WeatherWindowResult:
        ...
```

Use async only if consistent with the existing backend stack.

The architectural requirement is substitutability, not a specific Python mechanism.

---

# 21. Normalized errors

```text
WeatherProviderErrorCode
    INVALID_REQUEST
    UNSUPPORTED_VARIABLE
    UNSUPPORTED_RANGE
    DATA_UNAVAILABLE
    PROVIDER_UNAVAILABLE
    RATE_LIMITED
    TIMEOUT
    AUTHENTICATION_FAILED
    MALFORMED_RESPONSE
    UNKNOWN_PROVIDER_ERROR
```

Recommended normalized exception data:

```text
WeatherProviderError
    code
    provider_id
    retryable
    safe_message
    internal_cause?
```

`internal_cause` must not be exposed directly in farmer-facing responses.

---

# 22. Retry semantics

B1 only represents whether an error is retryable.

Examples:

```text
TIMEOUT              -> usually retryable
PROVIDER_UNAVAILABLE -> usually retryable
RATE_LIMITED         -> usually retryable

INVALID_REQUEST      -> not retryable
UNSUPPORTED_VARIABLE -> not retryable
UNSUPPORTED_RANGE    -> not retryable
```

The adapter/application layer owns retry count/backoff.

No uncontrolled retry loop belongs in the contract.

---

# 23. No silent provider fallback

B1 does not automatically change provider/dataset after failure.

A future fallback policy must explicitly preserve:

- provider identity,
- dataset identity,
- provenance,
- product behaviour.

---

# 24. Relationship to C1

B1 may eventually feed a reviewed derivation service.

It must not directly produce:

```text
MonsoonDelayStage
SowingMoistureStatus
```

Future:

```text
WeatherWindowResult
        ↓
reviewed derivation service
        ↓
SeasonContext
```

That service may then set:

```text
ContextSource.PROVIDER_DERIVED
```

---

# 25. Monsoon-delay boundary

B1 cannot conclude:

```text
ABOUT_4_WEEKS
ABOUT_6_WEEKS
```

It only returns normalized weather facts.

A future algorithm requires reviewed definitions for:

- monsoon onset,
- reference/normal onset,
- false onset,
- rainfall persistence,
- break periods,
- calendar interaction.

---

# 26. Sowing-moisture boundary

B1 cannot conclude:

```text
SowingMoistureStatus.READY
```

Daily rainfall alone is not identical to field sowing moisture.

No rainfall threshold is invented here.

---

# 27. Dry-spell/waterlogging boundary

B1 does not implement:

```text
dry-spell detector
terminal-drought detector
waterlogging detector
```

This remains consistent with C3 ScenarioAdvisory being deferred.

---

# 28. B2 Open-Meteo feasibility

Open-Meteo currently supports daily values corresponding to:

```text
precipitation sum
temperature min
temperature max
reference ET₀
```

and explicit timezone/unit selection.

Its returned coordinates can represent the selected weather grid cell rather than the exact requested coordinate.

B2 should therefore:

- explicitly request `Asia/Kolkata`,
- explicitly request metric units,
- map provider field names only inside the adapter,
- preserve resolved grid coordinates/elevation when available,
- classify recent past according to provider semantics rather than calling it "observed".

---

# 29. B2 cell-selection decision

Open-Meteo exposes provider-specific grid-cell selection behaviour.

That choice belongs in B2, not B1.

B2 must document whichever provider option it chooses and preserve the provider-resolved point.

Do not add Open-Meteo's `cell_selection` field to the B1 contract.

---

# 30. Caching/persistence

B1 mandates neither caching nor persistence.

Do not add Redis.

A later layer may choose to persist provider snapshots if exact audit/replay becomes necessary.

---

# 31. Security/privacy

Farm coordinates may become sensitive user/application data.

Guidance:

- do not log precise coordinates unnecessarily at INFO level,
- send only necessary location data to the provider,
- do not put coordinates into agronomic explanation text,
- do not expose internal provider errors to end users.

Authentication/user identity remains outside B1.

---

# 32. Suggested B1 implementation tests

When implemented, test:

1. valid latitude/longitude boundaries,
2. invalid coordinate ranges rejected,
3. no caller-supplied elevation field exists in V1,
4. start date after end date rejected,
5. timezone pinned to `Asia/Kolkata`,
6. requested variables are unique/immutable,
7. daily precipitation is mandatory,
8. unsupported optional variable can be rejected by provider capability validation,
9. precipitation cannot be negative,
10. missing precipitation remains `None`,
11. ET₀ cannot be negative,
12. temperature min cannot exceed max,
13. temporal position derives deterministically from `reference_date`,
14. temporal position is independent of data basis,
15. archived past forecast can be represented as `PAST + ARCHIVED_FORECAST`,
16. records are sorted,
17. duplicate dates rejected,
18. record outside requested range rejected,
19. complete/partial/empty required-data coverage is derived consistently,
20. missing mandatory precipitation is listed in `dates_missing_required_data`,
21. optional missing temperature can produce PARTIAL record while required-data coverage remains COMPLETE,
22. provenance does not duplicate requested location/timezone,
23. requested and provider-resolved points can differ,
24. retrieval timestamp is timezone-aware,
25. normalized errors include `UNSUPPORTED_VARIABLE`,
26. no monsoon-delay derivation exists,
27. no sowing-moisture derivation exists,
28. no soil-moisture field exists,
29. no Open-Meteo-specific field exists in B1,
30. no silent provider fallback exists.

---

# 33. Recommended module boundary

Conceptually:

```text
data_adapters/
    weather/
        contract.py
        models.py
        errors.py
        providers/
            open_meteo.py   # B2
```

Adapt to repository conventions.

B1 contains only provider-neutral models/contracts/errors.

---

# 34. Review decisions

| Question | Frozen V1 decision |
|---|---|
| Mandatory weather metric | **Daily precipitation only** |
| Optional temperature/ET₀ | **Supported, non-decisional** |
| Provider soil moisture | **Excluded** |
| Request location | **Coordinates + explicit source** |
| Caller-supplied elevation | **Excluded for V1** |
| Taluka/village-to-coordinate resolution | **Separate unresolved concern** |
| Request date model | **Explicit start/end/reference date** |
| Timezone | **Pinned to Asia/Kolkata** |
| Past/current/future classification | **Temporal position only; separate from data basis** |
| Reanalysis in B1 | **No; B3 owns it** |
| Archived forecast distinction | **Yes** |
| Missing precipitation | **None, never 0** |
| Provider fallback | **No silent fallback** |
| Exact forecast replay guaranteed | **No** |
| Duplicate request data in provenance | **No** |
| Provider-specific grid selection in B1 | **No; B2 concern** |

---

# 35. Open gaps after review

```text
B1-GAP-001
LocationContext/taluka/village -> trustworthy GeoPoint strategy

B3-GAP-001
Historical replay semantics:
realised weather/reanalysis vs forecast available at decision time
```

Neither gap blocks B1 implementation.

---

# 36. B1 freeze decision

**Status: `READY_TO_FREEZE` for V1.**

The reviewed contract now cleanly represents:

```text
where
+
which local dates
+
which normalized weather variables
+
how complete the returned data is
+
what provider/model basis produced it
```

without introducing agronomic interpretation or Open-Meteo-specific concepts into the domain boundary.
