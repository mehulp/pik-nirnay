"""B1 non-goal tests: things this contract must NOT contain or do.

Per docs/data/b1-weather-provider-contract.md section 32, items 26-30, and
the task's explicit non-goals list. These are structural/field-presence
checks, not source-text scans.
"""

import pkgutil

from app.modules.data_adapters.weather import contract, errors, models


def test_no_reanalysis_basis_in_b1():
    assert "REANALYSIS" not in {member.name for member in models.WeatherDataBasis}


def test_no_soil_moisture_or_other_excluded_variables():
    allowed = {"DAILY_PRECIPITATION", "DAILY_TEMPERATURE_MIN", "DAILY_TEMPERATURE_MAX", "DAILY_ET0"}
    assert {member.name for member in models.WeatherVariable} == allowed


def test_no_open_meteo_specific_field_names_in_records_or_request():
    forbidden = {
        "precipitation_sum",
        "temperature_2m_max",
        "temperature_2m_min",
        "et0_fao_evapotranspiration",
        "cell_selection",
    }
    all_fields: set[str] = set()
    for model in (
        models.GeoPoint,
        models.WeatherLocation,
        models.WeatherWindowRequest,
        models.DailyWeatherRecord,
        models.WeatherWindowResult,
        models.WeatherProvenance,
        models.WeatherProviderCapabilities,
    ):
        all_fields |= set(model.model_fields.keys())
    assert all_fields.isdisjoint(forbidden)


def test_no_monsoon_delay_or_sowing_moisture_types_imported_or_defined():
    # B1 must not import C1's MonsoonDelayStage/SowingMoistureStatus, let
    # alone derive them.
    module_source_names = set(vars(models).keys()) | set(vars(contract).keys()) | set(vars(errors).keys())
    assert "MonsoonDelayStage" not in module_source_names
    assert "SowingMoistureStatus" not in module_source_names


def test_no_scenario_or_dry_spell_detector_defined():
    weather_pkg_names: set[str] = set()
    for module in (models, contract, errors):
        weather_pkg_names |= set(vars(module).keys())
    forbidden_substrings = ("DrySpell", "Waterlog", "TerminalDrought", "ScenarioAdvisory", "RiskScore")
    for name in weather_pkg_names:
        for forbidden in forbidden_substrings:
            assert forbidden not in name


def test_no_location_resolver_in_weather_module():
    # No taluka/village/district -> coordinate function exists here
    # (B1-GAP-001 is explicitly left open).
    weather_pkg_names: set[str] = set()
    for module in (models, contract, errors):
        weather_pkg_names |= set(vars(module).keys())
    for name in weather_pkg_names:
        assert "resolve" not in name.lower()


def test_providers_is_the_only_addition_beyond_the_b1_core_files():
    # B2 legitimately adds a `providers/` subpackage (docs/data/
    # b2-open-meteo-adapter.md); this test now checks that B1's own three
    # files remain the only *direct* module files, and that no provider
    # module bypasses the `providers/` boundary.
    import app.modules.data_adapters.weather as weather_pkg

    submodule_names = {
        info.name for info in pkgutil.iter_modules(weather_pkg.__path__, prefix="")
    }
    assert submodule_names == {"models", "contract", "errors", "providers"}


def test_b1_core_files_do_not_import_open_meteo_directly():
    for module in (models, contract, errors):
        source_module_names = {getattr(value, "__module__", "") for value in vars(module).values()}
        assert not any("open_meteo" in name for name in source_module_names if name)


def test_no_http_client_dependency_imported_by_b1():
    for module in (models, contract, errors):
        source_module_names = {
            getattr(value, "__module__", "") for value in vars(module).values()
        }
        for banned in ("httpx", "requests", "aiohttp", "urllib3"):
            assert not any(name.startswith(banned) for name in source_module_names if name)


