"""B2 tests: structurally valid but incomplete provider data must produce a
valid B1 result, never a provider failure.

Per docs/data/b2-open-meteo-adapter.md section 30 and the task's section
31/40 ("Valid incomplete data").
"""

from datetime import date

from app.modules.data_adapters.weather.models import RecordCompleteness, RequiredDataCoverage, WeatherVariable

from .helpers import json_handler, make_payload, make_request, run_provider_call


def test_null_precipitation_produces_missing_coverage_not_a_provider_failure():
    request = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 10))
    payload = make_payload(times=["2027-07-10"], precipitation=[None])
    result = run_provider_call(json_handler(200, payload), request)  # must not raise
    assert result.records[0].precipitation_mm is None
    assert result.required_data_coverage == RequiredDataCoverage.EMPTY
    assert result.dates_missing_required_data == (date(2027, 7, 10),)


def test_omitted_date_produces_missing_coverage_not_a_provider_failure():
    request = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 11))
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])  # 11th omitted
    result = run_provider_call(json_handler(200, payload), request)  # must not raise
    assert result.required_data_coverage == RequiredDataCoverage.PARTIAL
    assert date(2027, 7, 11) in result.dates_missing_required_data


def test_null_optional_temperature_produces_incomplete_record_not_a_provider_failure():
    request = make_request(
        variables=frozenset({WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_TEMPERATURE_MIN}),
        start_date=date(2027, 7, 10),
        end_date=date(2027, 7, 10),
    )
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0], temperature_min=[None])
    result = run_provider_call(json_handler(200, payload), request)  # must not raise
    assert result.records[0].completeness == RecordCompleteness.PARTIAL
    assert result.required_data_coverage == RequiredDataCoverage.COMPLETE  # precipitation is all that matters here


def test_fully_empty_window_produces_empty_coverage_not_a_provider_failure():
    request = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 11))
    payload = make_payload(times=[], precipitation=[])
    result = run_provider_call(json_handler(200, payload), request)  # must not raise
    assert result.records == ()
    assert result.required_data_coverage == RequiredDataCoverage.EMPTY
    assert result.dates_missing_required_data == (date(2027, 7, 10), date(2027, 7, 11))
