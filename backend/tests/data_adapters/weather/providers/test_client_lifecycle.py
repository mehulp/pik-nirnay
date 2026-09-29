"""B2 tests: HTTP client ownership and timeout.

Per docs/data/b2-open-meteo-adapter.md sections 14-15, 34 ("Client
lifecycle").
"""

import asyncio

import httpx

from app.modules.data_adapters.weather.providers.open_meteo import (
    DEFAULT_TIMEOUT_SECONDS,
    OpenMeteoWeatherProvider,
)

from .helpers import fixed_clock, make_payload, make_request


def test_injected_client_is_not_closed_by_provider():
    async def scenario() -> bool:
        transport = httpx.MockTransport(
            lambda r: httpx.Response(200, json=make_payload(times=["2027-07-10"], precipitation=[1.0]))
        )
        client = httpx.AsyncClient(transport=transport)
        provider = OpenMeteoWeatherProvider(client, clock=fixed_clock)
        await provider.get_daily_weather(make_request())
        was_open_after_call = not client.is_closed
        await client.aclose()
        return was_open_after_call

    assert asyncio.run(scenario()) is True


def test_same_client_instance_is_reused_across_calls_never_recreated():
    async def scenario() -> None:
        calls: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            return httpx.Response(200, json=make_payload(times=["2027-07-10"], precipitation=[1.0]))

        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            provider = OpenMeteoWeatherProvider(client, clock=fixed_clock)
            assert provider._http_client is client
            await provider.get_daily_weather(make_request())
            await provider.get_daily_weather(make_request())  # a second, independent call
            assert provider._http_client is client  # never replaced
        assert len(calls) == 2  # one HTTP call per get_daily_weather call, no more

    asyncio.run(scenario())


def test_default_timeout_is_ten_seconds():
    assert DEFAULT_TIMEOUT_SECONDS == 10.0


def test_configured_timeout_is_passed_to_the_http_call():
    captured_kwargs: dict = {}

    class RecordingAsyncClient(httpx.AsyncClient):
        async def get(self, url, **kwargs):  # type: ignore[override]
            captured_kwargs.update(kwargs)
            return await super().get(url, **kwargs)

    async def scenario() -> None:
        transport = httpx.MockTransport(
            lambda r: httpx.Response(200, json=make_payload(times=["2027-07-10"], precipitation=[1.0]))
        )
        async with RecordingAsyncClient(transport=transport) as client:
            provider = OpenMeteoWeatherProvider(client, timeout_seconds=3.5, clock=fixed_clock)
            await provider.get_daily_weather(make_request())

    asyncio.run(scenario())
    assert captured_kwargs["timeout"] == 3.5
