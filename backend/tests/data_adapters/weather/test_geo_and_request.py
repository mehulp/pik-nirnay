"""B1 tests: GeoPoint/WeatherLocation and WeatherWindowRequest.

Per docs/data/b1-weather-provider-contract.md section 32, items 1-8.
"""

from datetime import date

import pytest
from pydantic import ValidationError

from app.modules.data_adapters.weather.models import (
    CoordinateSource,
    GeoPoint,
    WeatherLocation,
    WeatherVariable,
    WeatherWindowRequest,
)


def _location() -> WeatherLocation:
    return WeatherLocation(
        point=GeoPoint(latitude=18.2, longitude=76.1),
        coordinate_source=CoordinateSource.VILLAGE_CENTROID,
    )


def test_valid_coordinate_boundaries_accepted():
    for lat, lon in [(-90, -180), (90, 180), (0, 0), (18.2, 76.1)]:
        GeoPoint(latitude=lat, longitude=lon)


@pytest.mark.parametrize("lat,lon", [(-90.0001, 0), (90.0001, 0), (0, -180.0001), (0, 180.0001)])
def test_invalid_coordinate_ranges_rejected(lat, lon):
    with pytest.raises(ValidationError):
        GeoPoint(latitude=lat, longitude=lon)


def test_geopoint_has_no_caller_elevation_field():
    assert "elevation_m" not in GeoPoint.model_fields
    assert set(GeoPoint.model_fields) == {"latitude", "longitude"}


def test_location_label_is_optional_metadata():
    loc = _location()
    assert loc.location_label is None
    loc2 = WeatherLocation(
        point=GeoPoint(latitude=18.2, longitude=76.1),
        coordinate_source=CoordinateSource.UNKNOWN,
        location_label="Bhoom taluka approx.",
    )
    assert loc2.location_label == "Bhoom taluka approx."


def _request(**overrides) -> WeatherWindowRequest:
    defaults = dict(
        location=_location(),
        start_date=date(2027, 7, 10),
        end_date=date(2027, 7, 14),
        reference_date=date(2027, 7, 12),
        requested_variables=frozenset({WeatherVariable.DAILY_PRECIPITATION}),
    )
    defaults.update(overrides)
    return WeatherWindowRequest(**defaults)


def test_valid_date_range_accepted():
    req = _request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 10))
    assert req.start_date == req.end_date


def test_start_after_end_rejected():
    with pytest.raises(ValidationError):
        _request(start_date=date(2027, 7, 15), end_date=date(2027, 7, 10))


def test_reference_date_may_be_outside_requested_range_past_only():
    # end_date < reference_date: a "what already happened" request.
    req = _request(
        start_date=date(2027, 7, 1), end_date=date(2027, 7, 5), reference_date=date(2027, 7, 20)
    )
    assert req.end_date < req.reference_date


def test_reference_date_may_be_outside_requested_range_future_only():
    # start_date > reference_date: a "what's coming" request.
    req = _request(
        start_date=date(2027, 8, 1), end_date=date(2027, 8, 5), reference_date=date(2027, 7, 20)
    )
    assert req.start_date > req.reference_date


def test_timezone_is_pinned_to_asia_kolkata():
    req = _request()
    assert req.timezone == "Asia/Kolkata"
    with pytest.raises(ValidationError):
        _request(timezone="UTC")


def test_requested_variables_are_unique_and_immutable():
    req = _request(
        requested_variables=[
            WeatherVariable.DAILY_PRECIPITATION,
            WeatherVariable.DAILY_PRECIPITATION,
            WeatherVariable.DAILY_TEMPERATURE_MIN,
        ]
    )
    assert isinstance(req.requested_variables, frozenset)
    assert req.requested_variables == frozenset(
        {WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_TEMPERATURE_MIN}
    )
    with pytest.raises(AttributeError):
        req.requested_variables.add(WeatherVariable.DAILY_ET0)  # type: ignore[attr-defined]


def test_daily_precipitation_is_mandatory():
    with pytest.raises(ValidationError):
        _request(requested_variables=frozenset({WeatherVariable.DAILY_TEMPERATURE_MIN}))


def test_request_schema_does_not_encode_provider_capability_limits():
    forbidden = {
        "max_past_days",
        "max_future_days",
        "supported_variables",
        "supports_past",
        "supports_future",
        "supports_current_day",
    }
    assert forbidden.isdisjoint(WeatherWindowRequest.model_fields.keys())


def test_request_does_not_reject_past_or_future_range_on_its_own():
    # Provider-neutral: capability compatibility is a separate concern
    # (contract.validate_request_against_capabilities), not enforced here.
    _request(start_date=date(2020, 1, 1), end_date=date(2020, 1, 5), reference_date=date(2027, 7, 20))
    _request(start_date=date(2030, 1, 1), end_date=date(2030, 1, 5), reference_date=date(2027, 7, 20))


def test_request_is_frozen():
    req = _request()
    with pytest.raises(ValidationError):
        req.start_date = date(2000, 1, 1)  # type: ignore[misc]
