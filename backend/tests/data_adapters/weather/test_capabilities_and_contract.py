"""B1 tests: WeatherProviderCapabilities and the WeatherProvider contract.

Per docs/data/b1-weather-provider-contract.md section 32, items 8, 32-33.
"""

from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.data_adapters.weather.contract import (
    WeatherProvider,
    validate_request_against_capabilities,
)
from app.modules.data_adapters.weather.errors import WeatherProviderError, WeatherProviderErrorCode
from app.modules.data_adapters.weather.models import (
    CoordinateSource,
    GeoPoint,
    RequiredDataCoverage,
    WeatherLocation,
    WeatherProvenance,
    WeatherProviderCapabilities,
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
        requested_variables=frozenset({WeatherVariable.DAILY_PRECIPITATION}),
    )
    defaults.update(overrides)
    return WeatherWindowRequest(**defaults)


def _capabilities(**overrides) -> WeatherProviderCapabilities:
    defaults = dict(
        provider_id="test_provider",
        supported_variables=frozenset(
            {WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_TEMPERATURE_MIN}
        ),
        supports_past=True,
        supports_current_day=True,
        supports_future=True,
    )
    defaults.update(overrides)
    return WeatherProviderCapabilities(**defaults)


def test_supported_variables_is_immutable_and_unique():
    caps = _capabilities(
        supported_variables=[WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_PRECIPITATION]
    )
    assert caps.supported_variables == frozenset({WeatherVariable.DAILY_PRECIPITATION})
    with pytest.raises(AttributeError):
        caps.supported_variables.add(WeatherVariable.DAILY_ET0)  # type: ignore[attr-defined]


@pytest.mark.parametrize("field", ["max_past_days", "max_future_days"])
def test_negative_capability_day_limits_rejected(field):
    with pytest.raises(ValidationError):
        _capabilities(**{field: -1})


def test_zero_capability_day_limits_accepted():
    caps = _capabilities(max_past_days=0, max_future_days=0)
    assert caps.max_past_days == 0


def test_capability_day_limits_optional():
    caps = _capabilities()
    assert caps.max_past_days is None
    assert caps.max_future_days is None


def test_provider_id_must_be_non_empty():
    with pytest.raises(ValidationError):
        _capabilities(provider_id="")


def test_unsupported_variable_rejected():
    request = _request(
        requested_variables=frozenset({WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_ET0})
    )
    caps = _capabilities(
        supported_variables=frozenset({WeatherVariable.DAILY_PRECIPITATION})
    )
    with pytest.raises(WeatherProviderError) as exc_info:
        validate_request_against_capabilities(request, caps)
    assert exc_info.value.code == WeatherProviderErrorCode.UNSUPPORTED_VARIABLE


def test_unsupported_past_range_rejected():
    request = _request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 12), reference_date=date(2027, 7, 12))
    caps = _capabilities(supports_past=False)
    with pytest.raises(WeatherProviderError) as exc_info:
        validate_request_against_capabilities(request, caps)
    assert exc_info.value.code == WeatherProviderErrorCode.UNSUPPORTED_RANGE


def test_unsupported_future_range_rejected():
    request = _request(start_date=date(2027, 7, 12), end_date=date(2027, 7, 14), reference_date=date(2027, 7, 12))
    caps = _capabilities(supports_future=False)
    with pytest.raises(WeatherProviderError) as exc_info:
        validate_request_against_capabilities(request, caps)
    assert exc_info.value.code == WeatherProviderErrorCode.UNSUPPORTED_RANGE


def test_unsupported_current_day_rejected():
    request = _request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 14), reference_date=date(2027, 7, 12))
    caps = _capabilities(supports_current_day=False)
    with pytest.raises(WeatherProviderError) as exc_info:
        validate_request_against_capabilities(request, caps)
    assert exc_info.value.code == WeatherProviderErrorCode.UNSUPPORTED_RANGE


def test_max_past_days_exceeded_rejected():
    request = _request(start_date=date(2027, 7, 1), end_date=date(2027, 7, 5), reference_date=date(2027, 7, 12))
    caps = _capabilities(max_past_days=5)
    with pytest.raises(WeatherProviderError) as exc_info:
        validate_request_against_capabilities(request, caps)
    assert exc_info.value.code == WeatherProviderErrorCode.UNSUPPORTED_RANGE


def test_max_future_days_exceeded_rejected():
    request = _request(start_date=date(2027, 7, 20), end_date=date(2027, 7, 25), reference_date=date(2027, 7, 12))
    caps = _capabilities(max_future_days=3)
    with pytest.raises(WeatherProviderError) as exc_info:
        validate_request_against_capabilities(request, caps)
    assert exc_info.value.code == WeatherProviderErrorCode.UNSUPPORTED_RANGE


def test_compatible_request_passes_validation():
    request = _request()
    caps = _capabilities()
    validate_request_against_capabilities(request, caps)  # must not raise


def test_capability_validation_never_mutates_request():
    request = _request()
    caps = _capabilities(supports_future=False)
    dumped_before = request.model_dump()
    try:
        validate_request_against_capabilities(request, caps)
    except WeatherProviderError:
        pass
    assert request.model_dump() == dumped_before


# ---------------------------------------------------------------------------
# WeatherProvider Protocol
# ---------------------------------------------------------------------------


def test_weather_provider_protocol_is_structurally_checkable():
    class FakeProvider:
        @property
        def provider_id(self) -> str:
            return "fake"

        def capabilities(self) -> WeatherProviderCapabilities:
            return _capabilities(provider_id="fake")

        async def get_daily_weather(self, request: WeatherWindowRequest) -> WeatherWindowResult:
            return WeatherWindowResult(
                request=request,
                records=(),
                required_data_coverage=RequiredDataCoverage.EMPTY,
                dates_missing_required_data=(),
                provenance=WeatherProvenance(provider_id="fake", retrieved_at=datetime.now(timezone.utc)),
            )

    assert isinstance(FakeProvider(), WeatherProvider)


def test_object_missing_required_methods_does_not_satisfy_protocol():
    class NotAProvider:
        provider_id = "nope"

    assert not isinstance(NotAProvider(), WeatherProvider)
