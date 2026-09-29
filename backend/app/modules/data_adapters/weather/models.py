"""B1 — provider-neutral WeatherProvider domain models.

Authoritative source: docs/data/b1-weather-provider-contract.md (V0.2,
READY_TO_FREEZE).

This module defines only what Pik Nirnay may ask a near-current weather
provider and what normalized facts it may return. It must NOT (see the
doc's sections 2, 24-27):

- determine monsoon onset/delay or sowing-moisture readiness,
- detect dry spells, waterlogging or terminal drought,
- produce crop suitability/recommendation/risk output,
- contain any Open-Meteo-specific (or other provider-specific) field name.

Implementation note on derived vs. validated fields (see completion report
for full rationale, per the task's request to document this choice):
`DailyWeatherRecord.temporal_position`/`completeness` and
`WeatherWindowResult.required_data_coverage`/`dates_missing_required_data`
are all **derived, not merely validated**. A standalone `DailyWeatherRecord`
cannot know `request.reference_date`/`requested_variables` (section 12), so
its `temporal_position`/`completeness` are accepted as provisional input;
`WeatherWindowResult`'s "after" validator then authoritatively recomputes
both, and overwrites the stored records/fields via `object.__setattr__`
(safe on a frozen Pydantic v2 model - confirmed empirically before writing
this module). This makes it structurally impossible to end up with a valid
`WeatherWindowResult` whose four derived quantities contradict each other
or the request, which is the outcome the doc's section 16 asks for
("prefer one authoritative derivation path ... rather than four
independently supplied values that can contradict each other").
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Location (sections 6-8)
# ---------------------------------------------------------------------------


class GeoPoint(BaseModel):
    """WGS84 coordinates. No caller-supplied elevation in V1 (section 6) —
    provider-resolved elevation, if any, belongs only in `WeatherProvenance`.
    """

    model_config = ConfigDict(frozen=True)

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class CoordinateSource(str, Enum):
    """Section 7. How `GeoPoint` was obtained. B1 does not implement any
    taluka/village -> coordinate resolution itself (B1-GAP-001, section 8)
    — this enum only records provenance for whatever coordinate the caller
    supplies."""

    FIELD_COORDINATE = "FIELD_COORDINATE"
    VILLAGE_CENTROID = "VILLAGE_CENTROID"
    TALUKA_CENTROID = "TALUKA_CENTROID"
    GEOCODED = "GEOCODED"
    TEST_FIXTURE = "TEST_FIXTURE"
    UNKNOWN = "UNKNOWN"


class WeatherLocation(BaseModel):
    """Section 7. `location_label` is diagnostic/display metadata only —
    no weather or crop rule may depend on it."""

    model_config = ConfigDict(frozen=True)

    point: GeoPoint
    coordinate_source: CoordinateSource
    location_label: str | None = None


# ---------------------------------------------------------------------------
# Request (sections 5, 9)
# ---------------------------------------------------------------------------


class WeatherVariable(str, Enum):
    """Section 5. Exactly these four; DAILY_PRECIPITATION is the only
    mandatory V1 metric. Deliberately excludes soil moisture, soil
    temperature, precipitation probability, humidity, wind, weather code,
    cloud cover and solar radiation (section 5.3)."""

    DAILY_PRECIPITATION = "DAILY_PRECIPITATION"
    DAILY_TEMPERATURE_MIN = "DAILY_TEMPERATURE_MIN"
    DAILY_TEMPERATURE_MAX = "DAILY_TEMPERATURE_MAX"
    DAILY_ET0 = "DAILY_ET0"


# Pinned per section 9.3. A Literal (rather than a single-member enum) keeps
# this a plain, self-documenting "only this string is valid" constraint.
PINNED_TIMEZONE = "Asia/Kolkata"


class WeatherWindowRequest(BaseModel):
    """Section 9. Provider-neutral request correctness only — this model
    must never reject a request merely because some particular provider
    can't support an optional variable or a past/future range (section 8);
    that is `validate_request_against_capabilities`'s job (contract.py).
    """

    model_config = ConfigDict(frozen=True)

    location: WeatherLocation
    start_date: date
    end_date: date
    reference_date: date
    timezone: Literal["Asia/Kolkata"] = PINNED_TIMEZONE
    requested_variables: frozenset[WeatherVariable]

    @model_validator(mode="after")
    def _validate_range_and_variables(self) -> "WeatherWindowRequest":
        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")
        if WeatherVariable.DAILY_PRECIPITATION not in self.requested_variables:
            raise ValueError("requested_variables must include DAILY_PRECIPITATION")
        return self


# ---------------------------------------------------------------------------
# Temporal position vs. data basis (sections 10-11)
# ---------------------------------------------------------------------------


class TemporalPosition(str, Enum):
    """Section 10. A pure date relationship to `reference_date` — never a
    statement about how the value was produced (see `WeatherDataBasis`)."""

    PAST = "PAST"
    CURRENT_DAY = "CURRENT_DAY"
    FUTURE = "FUTURE"


class WeatherDataBasis(str, Enum):
    """Section 11. Deliberately excludes REANALYSIS (B3's concern). A PAST
    record may legitimately carry ARCHIVED_FORECAST — past does not imply
    OBSERVATION."""

    OBSERVATION = "OBSERVATION"
    MODEL_ESTIMATE = "MODEL_ESTIMATE"
    LIVE_FORECAST = "LIVE_FORECAST"
    ARCHIVED_FORECAST = "ARCHIVED_FORECAST"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Records (sections 12-13)
# ---------------------------------------------------------------------------


class RecordCompleteness(str, Enum):
    """Section 13. Relative to the request's `requested_variables` — see
    the module docstring for why this is treated as provisional on a bare
    `DailyWeatherRecord` and authoritatively recomputed by
    `WeatherWindowResult`."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"


class DailyWeatherRecord(BaseModel):
    """Section 12. Missing `precipitation_mm` must stay `None` — it must
    never be normalized to `0`."""

    model_config = ConfigDict(frozen=True)

    date: date
    temporal_position: TemporalPosition
    data_basis: WeatherDataBasis

    precipitation_mm: float | None = None
    temperature_min_c: float | None = None
    temperature_max_c: float | None = None
    et0_mm: float | None = None

    completeness: RecordCompleteness

    @field_validator("precipitation_mm")
    @classmethod
    def _precipitation_non_negative(cls, value: float | None) -> float | None:
        if value is not None and value < 0:
            raise ValueError("precipitation_mm must be >= 0 when provided")
        return value

    @field_validator("et0_mm")
    @classmethod
    def _et0_non_negative(cls, value: float | None) -> float | None:
        if value is not None and value < 0:
            raise ValueError("et0_mm must be >= 0 when provided")
        return value

    @model_validator(mode="after")
    def _validate_temperature_order(self) -> "DailyWeatherRecord":
        if (
            self.temperature_min_c is not None
            and self.temperature_max_c is not None
            and self.temperature_min_c > self.temperature_max_c
        ):
            raise ValueError("temperature_min_c must be <= temperature_max_c")
        return self


_VARIABLE_TO_RECORD_FIELD: dict[WeatherVariable, str] = {
    WeatherVariable.DAILY_PRECIPITATION: "precipitation_mm",
    WeatherVariable.DAILY_TEMPERATURE_MIN: "temperature_min_c",
    WeatherVariable.DAILY_TEMPERATURE_MAX: "temperature_max_c",
    WeatherVariable.DAILY_ET0: "et0_mm",
}


def _derive_temporal_position(record_date: date, reference_date: date) -> TemporalPosition:
    if record_date < reference_date:
        return TemporalPosition.PAST
    if record_date == reference_date:
        return TemporalPosition.CURRENT_DAY
    return TemporalPosition.FUTURE


def _derive_completeness(
    record: DailyWeatherRecord, requested_variables: frozenset[WeatherVariable]
) -> RecordCompleteness:
    present = sum(
        1
        for variable in requested_variables
        if getattr(record, _VARIABLE_TO_RECORD_FIELD[variable]) is not None
    )
    if present == len(requested_variables):
        return RecordCompleteness.COMPLETE
    if present == 0:
        return RecordCompleteness.MISSING
    return RecordCompleteness.PARTIAL


# ---------------------------------------------------------------------------
# Required-data coverage (sections 14-15)
# ---------------------------------------------------------------------------


class RequiredDataCoverage(str, Enum):
    """Section 14. Based only on DAILY_PRECIPITATION, independent of
    `RecordCompleteness` — a window can be COMPLETE here while individual
    records are PARTIAL because an optional variable is missing."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    EMPTY = "EMPTY"


# ---------------------------------------------------------------------------
# Provenance (sections 17-18)
# ---------------------------------------------------------------------------


class WeatherProvenance(BaseModel):
    """Section 17. Deliberately does not repeat `request.location` or
    `request.timezone` — the doc explicitly calls this duplication out."""

    model_config = ConfigDict(frozen=True)

    provider_id: str
    provider_dataset: str | None = None
    provider_model: str | None = None
    provider_run_id: str | None = None
    provider_run_initialized_at: datetime | None = None
    retrieved_at: datetime
    resolved_point: GeoPoint | None = None
    resolved_elevation_m: float | None = None

    @field_validator("provider_id")
    @classmethod
    def _provider_id_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("provider_id must be non-empty")
        return value

    @field_validator("retrieved_at")
    @classmethod
    def _retrieved_at_is_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("retrieved_at must be timezone-aware UTC")
        return value

    @field_validator("provider_run_initialized_at")
    @classmethod
    def _run_initialized_at_is_tz_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("provider_run_initialized_at must be timezone-aware")
        return value


# ---------------------------------------------------------------------------
# Result (section 16)
# ---------------------------------------------------------------------------


class WeatherWindowResult(BaseModel):
    """Section 16. See the module docstring: `required_data_coverage` and
    `dates_missing_required_data` are derived here, and every record's
    `temporal_position`/`completeness` is (re)derived here too, overriding
    whatever a caller supplied — this is the "one authoritative derivation
    path" the doc asks for.

    Structural invariants that are *validated* (rejected, not silently
    fixed) rather than derived: every record date falls inside the request
    range, no duplicate record dates, and records are in canonical
    ascending order. A provider adapter is expected to have already
    deduplicated/sorted before constructing this model (section 16).
    """

    model_config = ConfigDict(frozen=True)

    request: WeatherWindowRequest
    records: tuple[DailyWeatherRecord, ...]
    required_data_coverage: RequiredDataCoverage
    dates_missing_required_data: tuple[date, ...]
    provenance: WeatherProvenance

    @model_validator(mode="after")
    def _validate_and_derive(self) -> "WeatherWindowResult":
        request = self.request

        for record in self.records:
            if not (request.start_date <= record.date <= request.end_date):
                raise ValueError(
                    f"record date {record.date} falls outside requested range "
                    f"[{request.start_date}, {request.end_date}]"
                )

        record_dates = [record.date for record in self.records]
        if len(record_dates) != len(set(record_dates)):
            raise ValueError("duplicate record dates are not allowed")
        if record_dates != sorted(record_dates):
            raise ValueError("records must be in canonical ascending date order")

        corrected_records = tuple(
            record.model_copy(
                update={
                    "temporal_position": _derive_temporal_position(
                        record.date, request.reference_date
                    ),
                    "completeness": _derive_completeness(record, request.requested_variables),
                }
            )
            for record in self.records
        )
        object.__setattr__(self, "records", corrected_records)

        records_by_date = {record.date: record for record in corrected_records}
        missing_dates: list[date] = []
        any_present = False
        any_missing = False
        current = request.start_date
        while current <= request.end_date:
            record = records_by_date.get(current)
            if record is not None and record.precipitation_mm is not None:
                any_present = True
            else:
                any_missing = True
                missing_dates.append(current)
            current += timedelta(days=1)

        if not any_missing:
            coverage = RequiredDataCoverage.COMPLETE
        elif any_present:
            coverage = RequiredDataCoverage.PARTIAL
        else:
            coverage = RequiredDataCoverage.EMPTY

        object.__setattr__(self, "required_data_coverage", coverage)
        object.__setattr__(self, "dates_missing_required_data", tuple(missing_dates))

        return self


# ---------------------------------------------------------------------------
# Provider capabilities (section 19)
# ---------------------------------------------------------------------------


class WeatherProviderCapabilities(BaseModel):
    """Section 19. Integration capabilities, not agronomic facts. Never
    encode a specific provider's limits into the request schema itself —
    they belong here and are checked by
    `contract.validate_request_against_capabilities`."""

    model_config = ConfigDict(frozen=True)

    provider_id: str
    supported_variables: frozenset[WeatherVariable]
    supports_past: bool
    supports_current_day: bool
    supports_future: bool
    max_past_days: int | None = Field(default=None, ge=0)
    max_future_days: int | None = Field(default=None, ge=0)

    @field_validator("provider_id")
    @classmethod
    def _provider_id_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("provider_id must be non-empty")
        return value
