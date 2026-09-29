"""B2 tests: compatibility with the existing, unmodified B1 schema.

Per docs/data/b2-open-meteo-adapter.md section 27 and the task's section
18/40 ("B1 derived-field compatibility").
"""

from datetime import date

from app.modules.data_adapters.weather.models import (
    DailyWeatherRecord,
    RecordCompleteness,
    RequiredDataCoverage,
    TemporalPosition,
    WeatherDataBasis,
)
from app.modules.data_adapters.weather.providers.open_meteo import (
    _PROVISIONAL_COMPLETENESS,
    _PROVISIONAL_TEMPORAL_POSITION,
)

from .helpers import json_handler, make_payload, make_request, run_provider_call


def test_provider_constructs_records_without_any_b1_schema_change():
    # DailyWeatherRecord's constructor is used exactly as B1 defined it -
    # no new optional defaults, no relaxed required fields. This directly
    # exercises the same constructor B1's own tests use.
    record = DailyWeatherRecord(
        date=date(2027, 7, 10),
        temporal_position=_PROVISIONAL_TEMPORAL_POSITION,
        data_basis=WeatherDataBasis.ARCHIVED_FORECAST,
        precipitation_mm=5.0,
        completeness=_PROVISIONAL_COMPLETENESS,
    )
    assert record.precipitation_mm == 5.0


def test_weather_window_result_remains_authoritative_for_temporal_position():
    # The provisional temporal_position B2 supplies is PAST for every
    # record; WeatherWindowResult must still override it correctly relative
    # to the request's reference_date.
    request = make_request(start_date=date(2027, 7, 14), end_date=date(2027, 7, 14), reference_date=date(2027, 7, 10))
    payload = make_payload(times=["2027-07-14"], precipitation=[1.0])
    result = run_provider_call(json_handler(200, payload), request)
    assert _PROVISIONAL_TEMPORAL_POSITION == TemporalPosition.PAST  # B2's placeholder
    assert result.records[0].temporal_position == TemporalPosition.FUTURE  # B1's authoritative answer


def test_weather_window_result_remains_authoritative_for_completeness_and_coverage():
    request = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 10))
    payload = make_payload(times=["2027-07-10"], precipitation=[1.0])
    result = run_provider_call(json_handler(200, payload), request)
    assert _PROVISIONAL_COMPLETENESS == RecordCompleteness.MISSING  # B2's placeholder
    assert result.records[0].completeness == RecordCompleteness.COMPLETE  # B1's authoritative answer
    assert result.required_data_coverage == RequiredDataCoverage.COMPLETE
