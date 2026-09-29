"""B1 — the provider-neutral `WeatherProvider` interface and capability
validation.

Authoritative source: docs/data/b1-weather-provider-contract.md, sections
8, 19-22.

No concrete provider is implemented here (that is B2's job). This module
contains no HTTP client and makes no network calls.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Protocol, runtime_checkable

from app.modules.data_adapters.weather.errors import WeatherProviderError, WeatherProviderErrorCode
from app.modules.data_adapters.weather.models import (
    WeatherProviderCapabilities,
    WeatherWindowRequest,
    WeatherWindowResult,
)


@runtime_checkable
class WeatherProvider(Protocol):
    """Section 20. The architectural requirement is substitutability, not
    a specific Python mechanism — this Protocol is the provider-neutral
    shape any future adapter (e.g. B2's Open-Meteo adapter) must satisfy.
    """

    @property
    def provider_id(self) -> str: ...

    def capabilities(self) -> WeatherProviderCapabilities: ...

    async def get_daily_weather(self, request: WeatherWindowRequest) -> WeatherWindowResult: ...


def validate_request_against_capabilities(
    request: WeatherWindowRequest, capabilities: WeatherProviderCapabilities
) -> None:
    """Pure validation (section 8): checks `request` against one provider's
    declared `capabilities` and raises a normalized `WeatherProviderError`
    if incompatible. Never mutates anything and never makes a network call.

    `WeatherWindowRequest` itself must stay provider-neutral (section 9), so
    this — not the request schema — is where a specific provider's variable
    support and past/current/future/day-count limits are enforced.
    """
    unsupported_variables = request.requested_variables - capabilities.supported_variables
    if unsupported_variables:
        raise WeatherProviderError(
            code=WeatherProviderErrorCode.UNSUPPORTED_VARIABLE,
            provider_id=capabilities.provider_id,
            retryable=False,
            safe_message=(
                "Requested variable(s) not supported by this provider: "
                f"{sorted(variable.value for variable in unsupported_variables)}"
            ),
        )

    pivot = request.reference_date

    if request.start_date < pivot and not capabilities.supports_past:
        raise WeatherProviderError(
            code=WeatherProviderErrorCode.UNSUPPORTED_RANGE,
            provider_id=capabilities.provider_id,
            retryable=False,
            safe_message="This provider does not support past-dated requests.",
        )

    if request.end_date > pivot and not capabilities.supports_future:
        raise WeatherProviderError(
            code=WeatherProviderErrorCode.UNSUPPORTED_RANGE,
            provider_id=capabilities.provider_id,
            retryable=False,
            safe_message="This provider does not support future-dated requests.",
        )

    if (
        request.start_date <= pivot <= request.end_date
        and not capabilities.supports_current_day
    ):
        raise WeatherProviderError(
            code=WeatherProviderErrorCode.UNSUPPORTED_RANGE,
            provider_id=capabilities.provider_id,
            retryable=False,
            safe_message="This provider does not support current-day requests.",
        )

    if capabilities.max_past_days is not None:
        oldest_allowed = pivot - timedelta(days=capabilities.max_past_days)
        if request.start_date < oldest_allowed:
            raise WeatherProviderError(
                code=WeatherProviderErrorCode.UNSUPPORTED_RANGE,
                provider_id=capabilities.provider_id,
                retryable=False,
                safe_message=(
                    f"Requested start_date is more than {capabilities.max_past_days} "
                    "day(s) in the past, which this provider does not support."
                ),
            )

    if capabilities.max_future_days is not None:
        latest_allowed = pivot + timedelta(days=capabilities.max_future_days)
        if request.end_date > latest_allowed:
            raise WeatherProviderError(
                code=WeatherProviderErrorCode.UNSUPPORTED_RANGE,
                provider_id=capabilities.provider_id,
                retryable=False,
                safe_message=(
                    f"Requested end_date is more than {capabilities.max_future_days} "
                    "day(s) in the future, which this provider does not support."
                ),
            )
