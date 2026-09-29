"""B2 tests: malformed provider response handling.

Per docs/data/b2-open-meteo-adapter.md sections 20-26, 28, 34.
Every case here must map to WeatherProviderErrorCode.MALFORMED_RESPONSE.
"""

import httpx
import pytest

from app.modules.data_adapters.weather.errors import WeatherProviderError, WeatherProviderErrorCode
from app.modules.data_adapters.weather.models import WeatherVariable

from .helpers import make_payload, make_request, run_provider_call


def _assert_malformed(handler, request=None):
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, request or make_request())
    assert exc_info.value.code == WeatherProviderErrorCode.MALFORMED_RESPONSE
    return exc_info.value


def test_non_json_2xx_response():
    handler = lambda r: httpx.Response(200, content=b"not json at all {{{")
    _assert_malformed(handler)


def test_response_not_a_json_object():
    handler = lambda r: httpx.Response(200, json=[1, 2, 3])
    _assert_malformed(handler)


def test_missing_daily_field():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    del payload["daily"]
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_missing_daily_time():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    del payload["daily"]["time"]
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_requested_field_entirely_absent():
    request = make_request(
        variables=frozenset({WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_ET0})
    )
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])  # et0 never requested from provider
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler, request)


def test_mismatched_array_lengths():
    payload = make_payload(times=["2027-07-10", "2027-07-11"], precipitation=[1.0])  # length 1 vs 2
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_duplicate_dates_rejected():
    payload = make_payload(times=["2027-07-10", "2027-07-10"], precipitation=[1.0, 2.0])
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_invalid_iso_date_string_rejected():
    payload = make_payload(times=["2027-13-45"], precipitation=[1.0])
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_non_string_date_entry_rejected():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    payload["daily"]["time"] = [20270710]
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_out_of_order_dates_rejected():
    payload = make_payload(times=["2027-07-12", "2027-07-10"], precipitation=[1.0, 2.0])
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_incompatible_response_timezone_rejected():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0], timezone_name="UTC")
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_incorrect_utc_offset_rejected():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0], utc_offset_seconds=0)
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_missing_utc_offset_is_tolerated():
    # utc_offset_seconds is documented as sometimes absent; only verify it
    # when present (doc section 20/21 - "when provided, also verify...").
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0], utc_offset_seconds=None)
    handler = lambda r: httpx.Response(200, json=payload)
    result = run_provider_call(handler, make_request())
    assert result.records[0].precipitation_mm == 1.0


def test_incompatible_precipitation_unit_rejected():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    payload["daily_units"]["precipitation_sum"] = "inch"
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_incompatible_temperature_unit_rejected():
    request = make_request(
        variables=frozenset({WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_TEMPERATURE_MIN})
    )
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0], temperature_min=[20.0])
    payload["daily_units"]["temperature_2m_min"] = "°F"
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler, request)


def test_missing_unit_metadata_for_requested_field_rejected():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    del payload["daily_units"]["precipitation_sum"]
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_invalid_resolved_coordinate_rejected():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0], latitude=200.0, longitude=76.1)
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)


def test_non_numeric_elevation_rejected():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    payload["elevation"] = "not-a-number"
    handler = lambda r: httpx.Response(200, json=payload)
    _assert_malformed(handler)
