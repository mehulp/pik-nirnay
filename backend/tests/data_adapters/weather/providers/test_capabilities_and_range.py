"""B2 tests: declared capabilities and rolling-range behaviour.

Per docs/data/b2-open-meteo-adapter.md sections 3, 17, 34.

The key correctness property under test: the rolling past/future window
must be anchored to the *actual* current date (from the injected clock),
never to `request.reference_date`, which may be historical (e.g. a replay).
"""

from datetime import date, datetime, timezone

import httpx
import pytest

from app.modules.data_adapters.weather.errors import WeatherProviderError, WeatherProviderErrorCode
from app.modules.data_adapters.weather.models import WeatherVariable
from app.modules.data_adapters.weather.providers.open_meteo import OpenMeteoWeatherProvider

from .helpers import json_handler, make_payload, make_request, run_provider_call


def test_capabilities_declare_all_four_b1_variables():
    provider = OpenMeteoWeatherProvider(httpx.AsyncClient())
    caps = provider.capabilities()
    assert caps.supported_variables == frozenset(
        {
            WeatherVariable.DAILY_PRECIPITATION,
            WeatherVariable.DAILY_TEMPERATURE_MIN,
            WeatherVariable.DAILY_TEMPERATURE_MAX,
            WeatherVariable.DAILY_ET0,
        }
    )


def test_capabilities_support_past_current_and_future():
    caps = OpenMeteoWeatherProvider(httpx.AsyncClient()).capabilities()
    assert caps.supports_past is True
    assert caps.supports_current_day is True
    assert caps.supports_future is True


def test_capabilities_advertise_92_past_days():
    assert OpenMeteoWeatherProvider(httpx.AsyncClient()).capabilities().max_past_days == 92


def test_capabilities_advertise_16_forecast_days():
    assert OpenMeteoWeatherProvider(httpx.AsyncClient()).capabilities().max_future_days == 16


def test_capabilities_provider_id_is_open_meteo():
    assert OpenMeteoWeatherProvider(httpx.AsyncClient()).provider_id == "open_meteo"


def _fixed_clock(instant: datetime):
    return lambda: instant


def test_rolling_range_uses_actual_clock_not_reference_date():
    # reference_date is historical (2020); the actual clock says 2027-07-15.
    # A request for 2027-07-10..07-12 is only ~5 days before the *real*
    # current date, well inside the 92-day window - it must be accepted,
    # even though it is ~2700 days *after* reference_date.
    request = make_request(
        start_date=date(2027, 7, 10),
        end_date=date(2027, 7, 12),
        reference_date=date(2020, 1, 1),
    )
    handler = json_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]))
    clock = _fixed_clock(datetime(2027, 7, 15, tzinfo=timezone.utc))
    result = run_provider_call(handler, request, clock=clock)  # must not raise
    assert result.records[0].date == date(2027, 7, 10)


def test_obviously_impossible_past_range_rejected_before_http():
    # 200+ days before the real current date, far beyond the documented
    # 92-day past window - must be rejected without any HTTP call.
    request = make_request(start_date=date(2027, 1, 1), end_date=date(2027, 1, 2), reference_date=date(2027, 1, 1))
    calls: list = []

    def handler(req: httpx.Request) -> httpx.Response:
        calls.append(req)
        return httpx.Response(200, json=make_payload(times=["2027-01-01"], precipitation=[1.0]))

    clock = _fixed_clock(datetime(2027, 7, 15, tzinfo=timezone.utc))
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, request, clock=clock)
    assert exc_info.value.code == WeatherProviderErrorCode.UNSUPPORTED_RANGE
    assert calls == []  # no HTTP call was made


def test_obviously_impossible_future_range_rejected_before_http():
    request = make_request(start_date=date(2028, 6, 1), end_date=date(2028, 6, 2), reference_date=date(2028, 6, 1))
    calls: list = []

    def handler(req: httpx.Request) -> httpx.Response:
        calls.append(req)
        return httpx.Response(200, json=make_payload(times=["2028-06-01"], precipitation=[1.0]))

    clock = _fixed_clock(datetime(2027, 7, 15, tzinfo=timezone.utc))
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, request, clock=clock)
    assert exc_info.value.code == WeatherProviderErrorCode.UNSUPPORTED_RANGE
    assert calls == []


def test_ambiguous_exact_boundary_is_forwarded_to_provider_not_guessed():
    # A request landing right at the documented 92-day boundary is *not*
    # rejected client-side by an invented off-by-one rule - it is sent to
    # the provider, and only the provider's own response is authoritative.
    request = make_request(
        start_date=date(2027, 4, 15),  # exactly 92 days before the clock date below
        end_date=date(2027, 4, 15),
        reference_date=date(2027, 4, 15),
    )
    clock = _fixed_clock(datetime(2027, 7, 16, tzinfo=timezone.utc))  # 92 days after 2027-04-15
    calls: list = []

    def handler(req: httpx.Request) -> httpx.Response:
        calls.append(req)
        return httpx.Response(200, json=make_payload(times=["2027-04-15"], precipitation=[1.0]))

    run_provider_call(handler, request, clock=clock)
    assert len(calls) == 1  # request was forwarded to the provider, not rejected locally


def test_shared_b1_validation_still_runs_for_a_fully_supported_request():
    # The B2 adapter reuses validate_request_against_capabilities for
    # variable-support checking (with day-limits stripped before the
    # call, see module docstring); confirm that reused path does not
    # spuriously reject a request using every B1 variable Open-Meteo
    # actually supports.
    request = make_request(
        variables=frozenset(
            {
                WeatherVariable.DAILY_PRECIPITATION,
                WeatherVariable.DAILY_TEMPERATURE_MIN,
                WeatherVariable.DAILY_TEMPERATURE_MAX,
                WeatherVariable.DAILY_ET0,
            }
        ),
        start_date=date(2027, 7, 10),
        end_date=date(2027, 7, 10),
        reference_date=date(2027, 7, 10),
    )
    handler = json_handler(
        200,
        make_payload(
            times=["2027-07-10"],
            precipitation=[1.0],
            temperature_min=[20.0],
            temperature_max=[30.0],
            et0=[3.0],
        ),
    )
    clock = _fixed_clock(datetime(2027, 7, 15, tzinfo=timezone.utc))
    result = run_provider_call(handler, request, clock=clock)
    assert result.records[0].et0_mm == 3.0
