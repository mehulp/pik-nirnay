"""B1 tests: DailyWeatherRecord validation and WeatherWindowResult derivation.

Per docs/data/b1-weather-provider-contract.md section 32, items 9-24.
"""

from datetime import date, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.modules.data_adapters.weather.models import (
    CoordinateSource,
    DailyWeatherRecord,
    GeoPoint,
    RecordCompleteness,
    RequiredDataCoverage,
    TemporalPosition,
    WeatherDataBasis,
    WeatherLocation,
    WeatherProvenance,
    WeatherVariable,
    WeatherWindowRequest,
    WeatherWindowResult,
)


def _location() -> WeatherLocation:
    return WeatherLocation(
        point=GeoPoint(latitude=18.2, longitude=76.1),
        coordinate_source=CoordinateSource.VILLAGE_CENTROID,
    )


def _request(**overrides) -> WeatherWindowRequest:
    defaults = dict(
        location=_location(),
        start_date=date(2027, 7, 10),
        end_date=date(2027, 7, 14),
        reference_date=date(2027, 7, 12),
        requested_variables=frozenset(
            {WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_TEMPERATURE_MIN}
        ),
    )
    defaults.update(overrides)
    return WeatherWindowRequest(**defaults)


def _provenance(**overrides) -> WeatherProvenance:
    defaults = dict(provider_id="test_provider", retrieved_at=datetime.now(timezone.utc))
    defaults.update(overrides)
    return WeatherProvenance(**defaults)


def _record(day: int, **overrides) -> DailyWeatherRecord:
    defaults = dict(
        date=date(2027, 7, day),
        temporal_position=TemporalPosition.PAST,  # provisional; Result re-derives it
        data_basis=WeatherDataBasis.ARCHIVED_FORECAST,
        precipitation_mm=1.0,
        completeness=RecordCompleteness.MISSING,  # provisional; Result re-derives it
    )
    defaults.update(overrides)
    return DailyWeatherRecord(**defaults)


def _result(records, request=None, coverage=RequiredDataCoverage.EMPTY, missing=()):
    return WeatherWindowResult(
        request=request or _request(),
        records=records,
        required_data_coverage=coverage,
        dates_missing_required_data=missing,
        provenance=_provenance(),
    )


# ---------------------------------------------------------------------------
# DailyWeatherRecord field validation
# ---------------------------------------------------------------------------


def test_negative_precipitation_rejected():
    with pytest.raises(ValidationError):
        _record(10, precipitation_mm=-0.1)


def test_missing_precipitation_remains_none():
    record = _record(10, precipitation_mm=None)
    assert record.precipitation_mm is None


def test_negative_et0_rejected():
    with pytest.raises(ValidationError):
        _record(10, et0_mm=-1.0)


def test_valid_et0_accepted():
    record = _record(10, et0_mm=0.0)
    assert record.et0_mm == 0.0


def test_temperature_min_exceeding_max_rejected():
    with pytest.raises(ValidationError):
        _record(10, temperature_min_c=30.0, temperature_max_c=25.0)


def test_temperature_min_equal_max_accepted():
    record = _record(10, temperature_min_c=25.0, temperature_max_c=25.0)
    assert record.temperature_min_c == record.temperature_max_c


def test_past_plus_archived_forecast_is_valid():
    # Explicitly required by the doc: past does not imply OBSERVATION.
    record = _record(10, data_basis=WeatherDataBasis.ARCHIVED_FORECAST)
    result = _result([record])
    assert result.records[0].temporal_position == TemporalPosition.PAST
    assert result.records[0].data_basis == WeatherDataBasis.ARCHIVED_FORECAST


# ---------------------------------------------------------------------------
# TemporalPosition derivation (WeatherWindowResult level)
# ---------------------------------------------------------------------------


def test_temporal_position_past_derivation():
    result = _result([_record(10)])
    assert result.records[0].temporal_position == TemporalPosition.PAST


def test_temporal_position_current_day_derivation():
    result = _result([_record(12)])  # reference_date is the 12th
    assert result.records[0].temporal_position == TemporalPosition.CURRENT_DAY


def test_temporal_position_future_derivation():
    result = _result([_record(14)])
    assert result.records[0].temporal_position == TemporalPosition.FUTURE


def test_temporal_position_independent_of_data_basis():
    past_observation = _result([_record(10, data_basis=WeatherDataBasis.OBSERVATION)])
    past_archived = _result([_record(10, data_basis=WeatherDataBasis.ARCHIVED_FORECAST)])
    assert past_observation.records[0].temporal_position == TemporalPosition.PAST
    assert past_archived.records[0].temporal_position == TemporalPosition.PAST
    assert past_observation.records[0].data_basis != past_archived.records[0].data_basis


# ---------------------------------------------------------------------------
# Structural invariants on WeatherWindowResult.records
# ---------------------------------------------------------------------------


def test_duplicate_record_dates_rejected():
    with pytest.raises(ValidationError):
        _result([_record(10), _record(10)])


def test_record_outside_requested_range_rejected():
    with pytest.raises(ValidationError):
        _result([_record(20)])  # request window is the 10th-14th


def test_records_must_be_in_canonical_ascending_order():
    with pytest.raises(ValidationError):
        _result([_record(12), _record(10)])


def test_canonical_ascending_order_accepted():
    result = _result([_record(10), _record(12), _record(14)])
    assert [r.date for r in result.records] == [date(2027, 7, 10), date(2027, 7, 12), date(2027, 7, 14)]


# ---------------------------------------------------------------------------
# RecordCompleteness derivation
# ---------------------------------------------------------------------------


def test_record_completeness_complete_when_all_requested_variables_present():
    result = _result([_record(10, precipitation_mm=5.0, temperature_min_c=20.0)])
    assert result.records[0].completeness == RecordCompleteness.COMPLETE


def test_record_completeness_partial_when_some_requested_variables_missing():
    result = _result([_record(10, precipitation_mm=5.0, temperature_min_c=None)])
    assert result.records[0].completeness == RecordCompleteness.PARTIAL


def test_record_completeness_missing_when_no_requested_variable_present():
    result = _result([_record(10, precipitation_mm=None, temperature_min_c=None)])
    assert result.records[0].completeness == RecordCompleteness.MISSING


def test_missing_optional_temperature_can_coexist_with_complete_required_coverage():
    request = _request(
        requested_variables=frozenset(
            {WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_TEMPERATURE_MIN}
        ),
        start_date=date(2027, 7, 10),
        end_date=date(2027, 7, 10),
    )
    record = _record(10, precipitation_mm=5.0, temperature_min_c=None)
    result = _result([record], request=request)
    assert result.records[0].completeness == RecordCompleteness.PARTIAL
    assert result.required_data_coverage == RequiredDataCoverage.COMPLETE


# ---------------------------------------------------------------------------
# RequiredDataCoverage / dates_missing_required_data derivation
# ---------------------------------------------------------------------------


def _single_day_request(day: int) -> WeatherWindowRequest:
    return _request(start_date=date(2027, 7, day), end_date=date(2027, 7, day), reference_date=date(2027, 7, day))


def test_required_data_coverage_complete():
    request = _request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 11))
    records = [_record(10, precipitation_mm=1.0), _record(11, precipitation_mm=0.0)]
    result = _result(records, request=request)
    assert result.required_data_coverage == RequiredDataCoverage.COMPLETE
    assert result.dates_missing_required_data == ()


def test_required_data_coverage_partial():
    request = _request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 11))
    records = [_record(10, precipitation_mm=1.0), _record(11, precipitation_mm=None)]
    result = _result(records, request=request)
    assert result.required_data_coverage == RequiredDataCoverage.PARTIAL
    assert result.dates_missing_required_data == (date(2027, 7, 11),)


def test_required_data_coverage_empty():
    request = _request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 11))
    result = _result([], request=request)
    assert result.required_data_coverage == RequiredDataCoverage.EMPTY
    assert result.dates_missing_required_data == (date(2027, 7, 10), date(2027, 7, 11))


def test_omitted_date_appears_in_dates_missing_required_data():
    request = _request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 12))
    records = [_record(10, precipitation_mm=1.0), _record(12, precipitation_mm=2.0)]  # 11th omitted
    result = _result(records, request=request)
    assert date(2027, 7, 11) in result.dates_missing_required_data


def test_precipitation_none_date_appears_in_dates_missing_required_data():
    request = _request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 10))
    record = _record(10, precipitation_mm=None)
    result = _result([record], request=request)
    assert result.dates_missing_required_data == (date(2027, 7, 10),)
    # never silently treated as zero:
    assert result.records[0].precipitation_mm is None


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


def test_provenance_does_not_duplicate_request_location_or_timezone():
    assert "requested_location" not in WeatherProvenance.model_fields
    assert "location" not in WeatherProvenance.model_fields
    assert "timezone" not in WeatherProvenance.model_fields
    assert "requested_timezone" not in WeatherProvenance.model_fields


def test_requested_and_resolved_points_can_differ():
    requested_point = GeoPoint(latitude=18.2, longitude=76.1)
    resolved_point = GeoPoint(latitude=18.25, longitude=76.15)
    request = _request(
        location=WeatherLocation(point=requested_point, coordinate_source=CoordinateSource.VILLAGE_CENTROID)
    )
    provenance = _provenance(resolved_point=resolved_point, resolved_elevation_m=-5.0)
    result = _result([_record(10)], request=request)
    result = result.model_copy(update={"provenance": provenance})
    assert result.request.location.point != result.provenance.resolved_point
    assert result.provenance.resolved_elevation_m == -5.0  # below sea level is valid


def test_retrieval_timestamp_must_be_utc_aware():
    with pytest.raises(ValidationError):
        _provenance(retrieved_at=datetime(2027, 7, 12, 10, 0, 0))  # naive


def test_retrieval_timestamp_must_be_utc_not_just_any_offset():
    ist = timezone(timedelta(hours=5, minutes=30))
    with pytest.raises(ValidationError):
        _provenance(retrieved_at=datetime(2027, 7, 12, 10, 0, 0, tzinfo=ist))


def test_provider_run_initialized_at_must_be_tz_aware_if_present():
    with pytest.raises(ValidationError):
        _provenance(provider_run_initialized_at=datetime(2027, 7, 12, 0, 0, 0))


def test_provider_run_initialized_at_optional():
    provenance = _provenance()
    assert provenance.provider_run_initialized_at is None


def test_provider_id_must_be_non_empty():
    with pytest.raises(ValidationError):
        _provenance(provider_id="   ")
