"""B2 tests: response normalization into B1 models.

Per docs/data/b2-open-meteo-adapter.md sections 18-22, 34.
"""

from datetime import date

from app.modules.data_adapters.weather.models import WeatherVariable

from .helpers import json_handler, make_location, make_payload, make_request, run_provider_call


def test_precipitation_values_mapped():
    request = make_request()
    payload = make_payload(times=["2027-07-10", "2027-07-11"], precipitation=[5.0, 0.0])
    result = run_provider_call(json_handler(200, payload), request)
    assert [r.precipitation_mm for r in result.records] == [5.0, 0.0]


def test_temperature_min_and_max_mapped():
    request = make_request(
        variables=frozenset({WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_TEMPERATURE_MIN, WeatherVariable.DAILY_TEMPERATURE_MAX})
    )
    payload = make_payload(
        times=["2027-07-10"], precipitation=[1.0], temperature_min=[21.5], temperature_max=[31.2]
    )
    result = run_provider_call(json_handler(200, payload), request)
    record = result.records[0]
    assert record.temperature_min_c == 21.5
    assert record.temperature_max_c == 31.2


def test_et0_mapped():
    request = make_request(
        variables=frozenset({WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_ET0})
    )
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0], et0=[4.4])
    result = run_provider_call(json_handler(200, payload), request)
    assert result.records[0].et0_mm == 4.4


def test_null_element_maps_to_none_never_zero():
    request = make_request()
    payload = make_payload(times=["2027-07-10", "2027-07-11"], precipitation=[None, 2.0])
    result = run_provider_call(json_handler(200, payload), request)
    assert result.records[0].precipitation_mm is None
    assert result.records[1].precipitation_mm == 2.0


def test_omitted_requested_date_stays_omitted_not_synthesized():
    request = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 12))
    # Provider omits the 11th entirely.
    payload = make_payload(times=["2027-07-10", "2027-07-12"], precipitation=[1.0, 2.0])
    result = run_provider_call(json_handler(200, payload), request)
    assert [r.date for r in result.records] == [date(2027, 7, 10), date(2027, 7, 12)]
    assert date(2027, 7, 11) in result.dates_missing_required_data


def test_resolved_point_and_elevation_captured():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0], latitude=18.27, longitude=76.19, elevation=612.5)
    result = run_provider_call(json_handler(200, payload), make_request())
    assert result.provenance.resolved_point.latitude == 18.27
    assert result.provenance.resolved_point.longitude == 76.19
    assert result.provenance.resolved_elevation_m == 612.5


def test_requested_point_is_never_overwritten_by_resolved_point():
    location = make_location(lat=18.2, lon=76.1)
    request = make_request(location=location)
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0], latitude=18.9, longitude=76.9)
    result = run_provider_call(json_handler(200, payload), request)
    assert result.request.location.point.latitude == 18.2
    assert result.request.location.point.longitude == 76.1
    assert result.provenance.resolved_point.latitude == 18.9


def test_provenance_dataset_and_model_fields():
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    result = run_provider_call(json_handler(200, payload), make_request())
    assert result.provenance.provider_id == "open_meteo"
    assert result.provenance.provider_dataset == "weather_forecast_api"
    assert result.provenance.provider_model is None
    assert result.provenance.provider_run_id is None
    assert result.provenance.provider_run_initialized_at is None
