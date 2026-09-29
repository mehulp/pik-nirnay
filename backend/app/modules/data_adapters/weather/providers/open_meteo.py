"""B2 — Open-Meteo Weather Forecast API adapter.

Authoritative source: docs/data/b2-open-meteo-adapter.md (V0.2,
READY_TO_FREEZE). Implements the B1 `WeatherProvider` contract
(docs/data/b1-weather-provider-contract.md) for Open-Meteo's generic
`/v1/forecast` endpoint only. No historical/reanalysis provider, no
geocoding, no agronomic derivation, no retries, no caching/persistence.

B2-REQ-ATTRIBUTION: any future UI that displays weather data sourced from
Open-Meteo must show the required Open-Meteo attribution (e.g. "Weather
data by Open-Meteo.com", per Open-Meteo's CC BY 4.0-style licence terms).
This module adds no UI/attribution field to B1 — `provider_id="open_meteo"`
in `WeatherProvenance` is the mechanism the presentation layer uses to
know the source (doc section 5).

On reusing `validate_request_against_capabilities` (see the completion
report for full rationale): B1's helper checks `max_past_days`/
`max_future_days` relative to `request.reference_date`, which may be
historical (e.g. a 2023 replay). Open-Meteo's actual rolling
past/future window is anchored to the real current date, not to
`reference_date`. Calling the shared helper with those two fields intact
would therefore validate against the wrong pivot. This adapter reuses the
helper only for the dimensions where `reference_date` is irrelevant
(requested-variable support, and the `supports_past/current/future`
booleans — all `True` for this provider, so that check is a harmless
no-op here) by calling it with `max_past_days`/`max_future_days` stripped,
then separately runs `_validate_rolling_range` anchored to the actual
provider-local "today" (from the injected clock). B1 itself is untouched.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import httpx
from pydantic import ValidationError

from app.modules.data_adapters.weather.contract import validate_request_against_capabilities
from app.modules.data_adapters.weather.errors import WeatherProviderError, WeatherProviderErrorCode
from app.modules.data_adapters.weather.models import (
    DailyWeatherRecord,
    GeoPoint,
    RecordCompleteness,
    RequiredDataCoverage,
    TemporalPosition,
    WeatherDataBasis,
    WeatherProvenance,
    WeatherProviderCapabilities,
    WeatherVariable,
    WeatherWindowRequest,
    WeatherWindowResult,
)

PROVIDER_ID = "open_meteo"
DEFAULT_BASE_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_TIMEOUT_SECONDS = 10.0

_IST = ZoneInfo("Asia/Kolkata")
_EXPECTED_RESPONSE_TIMEZONE = "Asia/Kolkata"
_EXPECTED_UTC_OFFSET_SECONDS = 19800  # India Standard Time, UTC+5:30

# doc section 6 — only requested B1 variables are ever sent/parsed.
_VARIABLE_TO_PARAM: dict[WeatherVariable, str] = {
    WeatherVariable.DAILY_PRECIPITATION: "precipitation_sum",
    WeatherVariable.DAILY_TEMPERATURE_MIN: "temperature_2m_min",
    WeatherVariable.DAILY_TEMPERATURE_MAX: "temperature_2m_max",
    WeatherVariable.DAILY_ET0: "et0_fao_evapotranspiration",
}
_PARAM_TO_VARIABLE = {param: variable for variable, param in _VARIABLE_TO_PARAM.items()}

_EXPECTED_UNITS: dict[str, str] = {
    "precipitation_sum": "mm",
    "temperature_2m_min": "°C",
    "temperature_2m_max": "°C",
    "et0_fao_evapotranspiration": "mm",
}

# DailyWeatherRecord requires temporal_position/completeness at
# construction time, but a standalone record can't know
# request.reference_date/requested_variables (B1 doc section 12) - these
# are deliberately-arbitrary placeholders, always overwritten by
# WeatherWindowResult's authoritative derivation (see module docstring).
_PROVISIONAL_TEMPORAL_POSITION = TemporalPosition.PAST
_PROVISIONAL_COMPLETENESS = RecordCompleteness.MISSING


def _default_clock() -> datetime:
    return datetime.now(timezone.utc)


class OpenMeteoWeatherProvider:
    """Concrete `WeatherProvider` for Open-Meteo's generic Forecast API.

    HTTP client ownership: the caller supplies an `httpx.AsyncClient`
    (constructor injection). This provider never closes it - construct and
    close the client at the call site (application startup/shutdown, or a
    test fixture), the same way any other shared HTTP client in the
    application would be managed. No client is created per request/record.
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        clock: Callable[[], datetime] = _default_clock,
    ) -> None:
        self._http_client = http_client
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._clock = clock

    @property
    def provider_id(self) -> str:
        return PROVIDER_ID

    def capabilities(self) -> WeatherProviderCapabilities:
        # doc section 3 - published Open-Meteo Forecast API capability,
        # not an agricultural fact and not a free-tier call quota.
        return WeatherProviderCapabilities(
            provider_id=PROVIDER_ID,
            supported_variables=frozenset(_VARIABLE_TO_PARAM.keys()),
            supports_past=True,
            supports_current_day=True,
            supports_future=True,
            max_past_days=92,
            max_future_days=16,
        )

    async def get_daily_weather(self, request: WeatherWindowRequest) -> WeatherWindowResult:
        capabilities = self.capabilities()

        # Safe to reuse for variable support + the (always-True, so no-op)
        # past/current/future booleans; day-count limits are intentionally
        # stripped here - see module docstring.
        validate_request_against_capabilities(
            request,
            capabilities.model_copy(update={"max_past_days": None, "max_future_days": None}),
        )

        retrieved_at = self._clock()
        provider_local_today = retrieved_at.astimezone(_IST).date()

        _validate_rolling_range(request, provider_local_today, capabilities)

        params = _build_request_params(request)

        try:
            response = await self._http_client.get(
                self._base_url, params=params, timeout=self._timeout_seconds
            )
        except httpx.TimeoutException as exc:
            raise WeatherProviderError(
                code=WeatherProviderErrorCode.TIMEOUT,
                provider_id=PROVIDER_ID,
                retryable=True,
                safe_message="The weather provider did not respond in time.",
                internal_cause=exc,
            ) from exc
        except httpx.TransportError as exc:
            raise WeatherProviderError(
                code=WeatherProviderErrorCode.PROVIDER_UNAVAILABLE,
                provider_id=PROVIDER_ID,
                retryable=True,
                safe_message="The weather provider could not be reached.",
                internal_cause=exc,
            ) from exc

        _raise_for_http_status(response)

        try:
            payload = response.json()
        except ValueError as exc:
            raise WeatherProviderError(
                code=WeatherProviderErrorCode.MALFORMED_RESPONSE,
                provider_id=PROVIDER_ID,
                retryable=False,
                safe_message="The weather provider returned a response that was not valid JSON.",
                internal_cause=exc,
            ) from exc

        try:
            return _normalize_response(payload, request, retrieved_at, provider_local_today)
        except ValidationError as exc:
            raise WeatherProviderError(
                code=WeatherProviderErrorCode.MALFORMED_RESPONSE,
                provider_id=PROVIDER_ID,
                retryable=False,
                safe_message="The weather provider response did not pass normalized validation.",
                internal_cause=exc,
            ) from exc


def _validate_rolling_range(
    request: WeatherWindowRequest, provider_local_today: date, capabilities: WeatherProviderCapabilities
) -> None:
    """Open-Meteo-specific rolling-range check, anchored to the actual
    current date rather than `request.reference_date` (doc section 17).

    Only the range documented by Open-Meteo itself (`past_days: 0-92`,
    `forecast_days: 0-16`) is enforced here - an "obviously impossible
    range" pre-flight check. Exact boundary edge cases beyond these
    documented numbers are deliberately left for Open-Meteo itself to
    reject (doc section 3's "exact-date range caution"); this function
    does not attempt to invent finer-grained off-by-one behaviour.
    """
    if capabilities.max_past_days is not None:
        oldest_allowed = provider_local_today - timedelta(days=capabilities.max_past_days)
        if request.start_date < oldest_allowed:
            raise WeatherProviderError(
                code=WeatherProviderErrorCode.UNSUPPORTED_RANGE,
                provider_id=PROVIDER_ID,
                retryable=False,
                safe_message=(
                    f"Requested start_date is more than {capabilities.max_past_days} day(s) "
                    "before the current date, which this provider does not support."
                ),
            )

    if capabilities.max_future_days is not None:
        latest_allowed = provider_local_today + timedelta(days=capabilities.max_future_days)
        if request.end_date > latest_allowed:
            raise WeatherProviderError(
                code=WeatherProviderErrorCode.UNSUPPORTED_RANGE,
                provider_id=PROVIDER_ID,
                retryable=False,
                safe_message=(
                    f"Requested end_date is more than {capabilities.max_future_days} day(s) "
                    "after the current date, which this provider does not support."
                ),
            )


def _build_request_params(request: WeatherWindowRequest) -> dict[str, str]:
    daily_params = sorted(_VARIABLE_TO_PARAM[variable] for variable in request.requested_variables)
    return {
        "latitude": str(request.location.point.latitude),
        "longitude": str(request.location.point.longitude),
        "start_date": request.start_date.isoformat(),
        "end_date": request.end_date.isoformat(),
        "daily": ",".join(daily_params),
        "timezone": "Asia/Kolkata",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm",
        "timeformat": "iso8601",
        "cell_selection": "land",
    }


def _extract_provider_reason(response: httpx.Response) -> str | None:
    """For internal diagnostics only - never placed into `safe_message`."""
    try:
        body = response.json()
    except ValueError:
        return None
    if isinstance(body, dict) and isinstance(body.get("reason"), str):
        return body["reason"]
    return None


def _raise_for_http_status(response: httpx.Response) -> None:
    status = response.status_code
    if status < 400:
        return

    reason = _extract_provider_reason(response)
    internal_cause = RuntimeError(f"open-meteo HTTP {status}: {reason}") if reason else None

    if status == 429:
        raise WeatherProviderError(
            code=WeatherProviderErrorCode.RATE_LIMITED,
            provider_id=PROVIDER_ID,
            retryable=True,
            safe_message="The weather provider is rate-limiting requests.",
            internal_cause=internal_cause,
        )
    if 500 <= status < 600:
        raise WeatherProviderError(
            code=WeatherProviderErrorCode.PROVIDER_UNAVAILABLE,
            provider_id=PROVIDER_ID,
            retryable=True,
            safe_message="The weather provider is temporarily unavailable.",
            internal_cause=internal_cause,
        )
    if status == 400:
        # doc section 30: a narrowly-tested reason-string range mapping is
        # allowed but not required; without confirmed implementation
        # evidence for Open-Meteo's exact wording, plain INVALID_REQUEST is
        # the documented sufficient fallback - avoids fragile substring
        # classification.
        raise WeatherProviderError(
            code=WeatherProviderErrorCode.INVALID_REQUEST,
            provider_id=PROVIDER_ID,
            retryable=False,
            safe_message="The weather provider rejected this request.",
            internal_cause=internal_cause,
        )
    if status == 401:
        raise WeatherProviderError(
            code=WeatherProviderErrorCode.AUTHENTICATION_FAILED,
            provider_id=PROVIDER_ID,
            retryable=False,
            safe_message="The weather provider rejected the request credentials.",
            internal_cause=internal_cause,
        )
    if status == 403:
        # The free V1 endpoint requires no authentication, so a 403 is not
        # automatically an authentication failure (doc section 28).
        raise WeatherProviderError(
            code=WeatherProviderErrorCode.UNKNOWN_PROVIDER_ERROR,
            provider_id=PROVIDER_ID,
            retryable=False,
            safe_message="The weather provider denied this request.",
            internal_cause=internal_cause,
        )
    raise WeatherProviderError(
        code=WeatherProviderErrorCode.UNKNOWN_PROVIDER_ERROR,
        provider_id=PROVIDER_ID,
        retryable=False,
        safe_message="The weather provider returned an unexpected error.",
        internal_cause=internal_cause,
    )


def _malformed(message: str) -> WeatherProviderError:
    return WeatherProviderError(
        code=WeatherProviderErrorCode.MALFORMED_RESPONSE,
        provider_id=PROVIDER_ID,
        retryable=False,
        safe_message=message,
    )


def _normalize_response(
    payload: object,
    request: WeatherWindowRequest,
    retrieved_at: datetime,
    provider_local_today: date,
) -> WeatherWindowResult:
    if not isinstance(payload, dict):
        raise _malformed("The weather provider response was not a JSON object.")

    response_timezone = payload.get("timezone")
    if response_timezone != _EXPECTED_RESPONSE_TIMEZONE:
        raise _malformed("The weather provider response timezone did not match the requested timezone.")

    utc_offset = payload.get("utc_offset_seconds")
    if utc_offset is not None and utc_offset != _EXPECTED_UTC_OFFSET_SECONDS:
        raise _malformed("The weather provider response UTC offset did not match India Standard Time.")

    daily = payload.get("daily")
    if not isinstance(daily, dict):
        raise _malformed("The weather provider response was missing the 'daily' field.")

    times = daily.get("time")
    if not isinstance(times, list):
        raise _malformed("The weather provider response was missing 'daily.time'.")

    daily_units = payload.get("daily_units")
    if not isinstance(daily_units, dict):
        raise _malformed("The weather provider response was missing 'daily_units'.")

    requested_params = sorted(_VARIABLE_TO_PARAM[variable] for variable in request.requested_variables)

    value_arrays: dict[str, list] = {}
    for param in requested_params:
        if param not in daily:
            raise _malformed(f"The weather provider response was missing requested field '{param}'.")
        array = daily[param]
        if not isinstance(array, list):
            raise _malformed(f"The weather provider field '{param}' was not an array.")
        if len(array) != len(times):
            raise _malformed(f"The weather provider field '{param}' length did not match 'daily.time'.")
        value_arrays[param] = array

        unit = daily_units.get(param)
        if unit != _EXPECTED_UNITS[param]:
            raise _malformed(f"The weather provider field '{param}' had an unexpected unit ({unit!r}).")

    parsed_dates: list[date] = []
    for raw in times:
        if not isinstance(raw, str):
            raise _malformed("The weather provider 'daily.time' array contained a non-string entry.")
        try:
            parsed_dates.append(date.fromisoformat(raw))
        except ValueError as exc:
            raise _malformed(
                f"The weather provider 'daily.time' array contained an invalid date ({raw!r})."
            ) from exc

    if len(parsed_dates) != len(set(parsed_dates)):
        raise _malformed("The weather provider response contained duplicate dates.")

    if parsed_dates != sorted(parsed_dates):
        raise _malformed("The weather provider response dates were not in ascending order.")

    records = []
    for index, record_date in enumerate(parsed_dates):
        field_values = {
            _PARAM_TO_VARIABLE[param]: array[index] for param, array in value_arrays.items()
        }
        data_basis = (
            WeatherDataBasis.ARCHIVED_FORECAST
            if record_date < provider_local_today
            else WeatherDataBasis.LIVE_FORECAST
        )
        records.append(
            DailyWeatherRecord(
                date=record_date,
                temporal_position=_PROVISIONAL_TEMPORAL_POSITION,
                data_basis=data_basis,
                precipitation_mm=field_values.get(WeatherVariable.DAILY_PRECIPITATION),
                temperature_min_c=field_values.get(WeatherVariable.DAILY_TEMPERATURE_MIN),
                temperature_max_c=field_values.get(WeatherVariable.DAILY_TEMPERATURE_MAX),
                et0_mm=field_values.get(WeatherVariable.DAILY_ET0),
                completeness=_PROVISIONAL_COMPLETENESS,
            )
        )

    resolved_point = None
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    if latitude is not None or longitude is not None:
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise _malformed("The weather provider returned an incomplete resolved coordinate.")
        resolved_point = GeoPoint(latitude=latitude, longitude=longitude)

    resolved_elevation = payload.get("elevation")
    if resolved_elevation is not None and not isinstance(resolved_elevation, (int, float)):
        raise _malformed("The weather provider returned a non-numeric elevation.")

    provenance = WeatherProvenance(
        provider_id=PROVIDER_ID,
        provider_dataset="weather_forecast_api",
        provider_model=None,
        provider_run_id=None,
        provider_run_initialized_at=None,
        retrieved_at=retrieved_at,
        resolved_point=resolved_point,
        resolved_elevation_m=float(resolved_elevation) if resolved_elevation is not None else None,
    )

    # required_data_coverage/dates_missing_required_data are provisional -
    # WeatherWindowResult authoritatively (re)derives them, per B1 design.
    return WeatherWindowResult(
        request=request,
        records=tuple(records),
        required_data_coverage=RequiredDataCoverage.EMPTY,
        dates_missing_required_data=(),
        provenance=provenance,
    )
