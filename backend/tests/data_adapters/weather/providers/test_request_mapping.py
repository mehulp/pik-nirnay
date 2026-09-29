"""B2 tests: HTTP request mapping.

Per docs/data/b2-open-meteo-adapter.md section 34 ("Request mapping").
"""

from datetime import date
from urllib.parse import parse_qs, urlparse

from app.modules.data_adapters.weather.models import WeatherVariable
from app.modules.data_adapters.weather.providers.open_meteo import DEFAULT_BASE_URL

from .helpers import capturing_handler, make_payload, make_request, run_provider_call


def _query_params(captured_request) -> dict[str, str]:
    parsed = urlparse(str(captured_request.url))
    return {key: values[0] for key, values in parse_qs(parsed.query).items()}


def test_latitude_and_longitude_mapped_exactly():
    request = make_request()  # default lat=18.2, lon=76.1
    captured: list = []
    handler = capturing_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]), captured)
    run_provider_call(handler, request)
    params = _query_params(captured[0])
    assert params["latitude"] == "18.2"
    assert params["longitude"] == "76.1"


def test_exact_start_and_end_dates_used_not_past_days_or_forecast_days():
    request = make_request(start_date=date(2027, 7, 10), end_date=date(2027, 7, 14))
    captured: list = []
    handler = capturing_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]), captured)
    run_provider_call(handler, request)
    params = _query_params(captured[0])
    assert params["start_date"] == "2027-07-10"
    assert params["end_date"] == "2027-07-14"
    assert "past_days" not in params
    assert "forecast_days" not in params


def test_timezone_is_asia_kolkata():
    captured: list = []
    handler = capturing_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]), captured)
    run_provider_call(handler, make_request())
    assert _query_params(captured[0])["timezone"] == "Asia/Kolkata"


def test_temperature_unit_is_celsius():
    captured: list = []
    handler = capturing_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]), captured)
    run_provider_call(handler, make_request())
    assert _query_params(captured[0])["temperature_unit"] == "celsius"


def test_precipitation_unit_is_mm():
    captured: list = []
    handler = capturing_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]), captured)
    run_provider_call(handler, make_request())
    assert _query_params(captured[0])["precipitation_unit"] == "mm"


def test_timeformat_is_iso8601():
    captured: list = []
    handler = capturing_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]), captured)
    run_provider_call(handler, make_request())
    assert _query_params(captured[0])["timeformat"] == "iso8601"


def test_cell_selection_is_land():
    captured: list = []
    handler = capturing_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]), captured)
    run_provider_call(handler, make_request())
    assert _query_params(captured[0])["cell_selection"] == "land"


def test_only_requested_daily_variables_are_sent():
    request = make_request(
        variables=frozenset({WeatherVariable.DAILY_PRECIPITATION, WeatherVariable.DAILY_TEMPERATURE_MAX})
    )
    captured: list = []
    handler = capturing_handler(
        200,
        make_payload(times=["2027-07-10"], precipitation=[1.0], temperature_max=[30.0]),
        captured,
    )
    run_provider_call(handler, request)
    daily_param = _query_params(captured[0])["daily"]
    requested = set(daily_param.split(","))
    assert requested == {"precipitation_sum", "temperature_2m_max"}


def test_no_excluded_weather_fields_ever_requested():
    request = make_request(
        variables=frozenset(
            {
                WeatherVariable.DAILY_PRECIPITATION,
                WeatherVariable.DAILY_TEMPERATURE_MIN,
                WeatherVariable.DAILY_TEMPERATURE_MAX,
                WeatherVariable.DAILY_ET0,
            }
        )
    )
    captured: list = []
    handler = capturing_handler(
        200,
        make_payload(
            times=["2027-07-10"],
            precipitation=[1.0],
            temperature_min=[20.0],
            temperature_max=[30.0],
            et0=[3.0],
        ),
        captured,
    )
    run_provider_call(handler, request)
    daily_fields = set(_query_params(captured[0])["daily"].split(","))
    forbidden = {
        "soil_moisture_0_1cm",
        "precipitation_probability_max",
        "relative_humidity_2m_max",
        "wind_speed_10m_max",
        "weather_code",
        "cloud_cover_mean",
        "shortwave_radiation_sum",
        "soil_temperature_0cm",
    }
    assert daily_fields.isdisjoint(forbidden)


def test_no_explicit_model_parameter_sent():
    captured: list = []
    handler = capturing_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]), captured)
    run_provider_call(handler, make_request())
    assert "models" not in _query_params(captured[0])


def test_default_base_url_is_v1_forecast_endpoint():
    assert DEFAULT_BASE_URL == "https://api.open-meteo.com/v1/forecast"
    captured: list = []
    handler = capturing_handler(200, make_payload(times=["2027-07-10"], precipitation=[1.0]), captured)
    run_provider_call(handler, make_request())
    assert str(captured[0].url).startswith(DEFAULT_BASE_URL)
