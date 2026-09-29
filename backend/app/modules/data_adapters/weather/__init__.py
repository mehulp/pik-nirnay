"""Weather provider adapters (e.g. Open-Meteo, IMD).

B1 (provider-neutral contract) is implemented, per
docs/data/b1-weather-provider-contract.md:

- `models.py` — GeoPoint, WeatherLocation, WeatherWindowRequest,
  DailyWeatherRecord, WeatherWindowResult, WeatherProvenance,
  WeatherProviderCapabilities, and their supporting enums.
- `contract.py` — the `WeatherProvider` Protocol and
  `validate_request_against_capabilities`.
- `errors.py` — `WeatherProviderErrorCode` / `WeatherProviderError`.

B2 (Open-Meteo adapter) is implemented in `providers/open_meteo.py`, per
docs/data/b2-open-meteo-adapter.md — `OpenMeteoWeatherProvider`, an
`httpx.AsyncClient`-based `WeatherProvider`. It is the only concrete
provider in this package; no historical/reanalysis provider, geocoder, or
other weather source is implemented.
"""
