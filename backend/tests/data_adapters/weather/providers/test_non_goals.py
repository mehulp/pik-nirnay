"""B2 non-goal tests.

Per docs/data/b2-open-meteo-adapter.md section 37 and the task's explicit
non-goals list. Structural/behavioural checks, not source-text scans.
"""

import pkgutil

from app.modules.data_adapters.weather import providers
from app.modules.data_adapters.weather.providers import open_meteo


def _public_names(module) -> set[str]:
    # Excludes Python's own module dunders (__cached__, __loader__, etc.),
    # which are not application-defined names.
    return {name for name in vars(module).keys() if not name.startswith("__")}


def test_no_other_provider_module_exists():
    submodule_names = {info.name for info in pkgutil.iter_modules(providers.__path__)}
    assert submodule_names == {"open_meteo"}


def test_no_geocoder_or_location_resolution_function_defined():
    for name in _public_names(open_meteo):
        assert "geocode" not in name.lower()
        assert "resolve_taluka" not in name.lower()
        assert "resolve_village" not in name.lower()


def test_no_historical_or_reanalysis_client_defined():
    names = {name.lower() for name in _public_names(open_meteo)}
    for forbidden in ("historical", "reanalysis", "previousrun", "singlerun", "climateapi"):
        assert not any(forbidden in name for name in names)


def test_no_retry_or_backoff_mechanism_defined():
    names = {name.lower() for name in _public_names(open_meteo)}
    for forbidden in ("retry", "backoff", "tenacity"):
        assert not any(forbidden in name for name in names)


def test_no_provider_fallback_mechanism_defined():
    names = {name.lower() for name in _public_names(open_meteo)}
    assert not any("fallback" in name for name in names)


def test_no_cache_or_persistence_defined():
    names = {name.lower() for name in _public_names(open_meteo)}
    for forbidden in ("cache", "redis", "persist", "snapshot", "dbsession"):
        assert not any(forbidden in name for name in names)
    module_source_names = {getattr(value, "__module__", "") for value in vars(open_meteo).values()}
    for banned in ("redis", "sqlalchemy"):
        assert not any(name.startswith(banned) for name in module_source_names if name)


def test_no_monsoon_or_sowing_derivation_imported():
    names = _public_names(open_meteo)
    assert "MonsoonDelayStage" not in names
    assert "SowingMoistureStatus" not in names


def test_no_crop_or_risk_logic_imported():
    names = _public_names(open_meteo)
    for forbidden in ("CropId", "CropOptionId", "DecisionRule", "RiskScore"):
        assert forbidden not in names


def test_no_commercial_endpoint_or_api_key_support():
    source_globals = vars(open_meteo)
    assert "customer-api.open-meteo.com" not in str(source_globals.get("DEFAULT_BASE_URL", ""))
    for name in _public_names(open_meteo):
        assert "api_key" not in name.lower()
        assert "apikey" not in name.lower()
