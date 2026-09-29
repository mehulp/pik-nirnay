"""Shared test helpers for the B2 Open-Meteo adapter tests.

No test in this package makes a real network call: every HTTP interaction
goes through `httpx.MockTransport`.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from datetime import date, datetime, timezone

import httpx

from app.modules.data_adapters.weather.models import (
    CoordinateSource,
    GeoPoint,
    WeatherLocation,
    WeatherVariable,
    WeatherWindowRequest,
    WeatherWindowResult,
)
from app.modules.data_adapters.weather.providers.open_meteo import OpenMeteoWeatherProvider

Handler = Callable[[httpx.Request], httpx.Response]

# A fixed, arbitrary "now" used by every test that doesn't care about
# clock-specific behaviour (request-mapping, normalization, malformed-
# response, error-mapping, client-lifecycle, valid-incomplete-data tests).
# Using a fixed instant - rather than the real wall clock - keeps those
# tests deterministic regardless of which real-world date the suite runs
# on. Tests that specifically exercise clock/range/data-basis behaviour
# (test_capabilities_and_range.py, test_data_basis.py,
# test_b1_compatibility.py) always pass their own explicit `clock`.
FIXED_CLOCK_INSTANT = datetime(2027, 7, 20, 12, 0, tzinfo=timezone.utc)


def fixed_clock() -> datetime:
    return FIXED_CLOCK_INSTANT


def make_location(lat: float = 18.2, lon: float = 76.1) -> WeatherLocation:
    return WeatherLocation(
        point=GeoPoint(latitude=lat, longitude=lon),
        coordinate_source=CoordinateSource.TEST_FIXTURE,
    )


def make_request(
    *,
    start_date: date = date(2027, 7, 10),
    end_date: date = date(2027, 7, 12),
    reference_date: date = date(2027, 7, 12),
    variables: frozenset[WeatherVariable] = frozenset({WeatherVariable.DAILY_PRECIPITATION}),
    location: WeatherLocation | None = None,
) -> WeatherWindowRequest:
    # These defaults sit safely inside FIXED_CLOCK_INSTANT's (2027-07-20)
    # rolling past/future window, so tests that don't care about the exact
    # date can rely on run_provider_call's default fixed clock and never
    # hit the real-world rolling-range check.
    return WeatherWindowRequest(
        location=location or make_location(),
        start_date=start_date,
        end_date=end_date,
        reference_date=reference_date,
        requested_variables=variables,
    )


def make_payload(
    *,
    times: list[str],
    precipitation: list | None = None,
    temperature_min: list | None = None,
    temperature_max: list | None = None,
    et0: list | None = None,
    latitude: float = 18.25,
    longitude: float = 76.15,
    elevation: float = 615.0,
    timezone_name: str = "Asia/Kolkata",
    utc_offset_seconds: int | None = 19800,
) -> dict:
    daily: dict[str, list] = {"time": times}
    units: dict[str, str] = {"time": "iso8601"}
    if precipitation is not None:
        daily["precipitation_sum"] = precipitation
        units["precipitation_sum"] = "mm"
    if temperature_min is not None:
        daily["temperature_2m_min"] = temperature_min
        units["temperature_2m_min"] = "°C"
    if temperature_max is not None:
        daily["temperature_2m_max"] = temperature_max
        units["temperature_2m_max"] = "°C"
    if et0 is not None:
        daily["et0_fao_evapotranspiration"] = et0
        units["et0_fao_evapotranspiration"] = "mm"

    payload = {
        "latitude": latitude,
        "longitude": longitude,
        "elevation": elevation,
        "timezone": timezone_name,
        "daily_units": units,
        "daily": daily,
    }
    if utc_offset_seconds is not None:
        payload["utc_offset_seconds"] = utc_offset_seconds
    return payload


def json_handler(status_code: int, payload: object) -> Handler:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=payload)

    return handler


def capturing_handler(status_code: int, payload: object, sink: list[httpx.Request]) -> Handler:
    def handler(request: httpx.Request) -> httpx.Response:
        sink.append(request)
        return httpx.Response(status_code, json=payload)

    return handler


def run_provider_call(
    handler: Handler,
    request: WeatherWindowRequest,
    *,
    clock: Callable[[], datetime] | None = None,
    timeout_seconds: float | None = None,
    base_url: str | None = None,
) -> WeatherWindowResult:
    async def _run() -> WeatherWindowResult:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            kwargs: dict = {"clock": clock if clock is not None else fixed_clock}
            if timeout_seconds is not None:
                kwargs["timeout_seconds"] = timeout_seconds
            if base_url is not None:
                kwargs["base_url"] = base_url
            provider = OpenMeteoWeatherProvider(client, **kwargs)
            return await provider.get_daily_weather(request)

    return asyncio.run(_run())
