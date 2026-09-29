"""B2 tests: transport/HTTP error mapping to normalized B1 errors.

Per docs/data/b2-open-meteo-adapter.md sections 28-29, 34.
"""

import httpx
import pytest

from app.modules.data_adapters.weather.errors import WeatherProviderError, WeatherProviderErrorCode

from .helpers import make_request, run_provider_call


def _raising_handler(exc: Exception):
    def handler(request: httpx.Request):
        raise exc

    return handler


def test_timeout_maps_to_timeout_retryable():
    handler = _raising_handler(httpx.ReadTimeout("timed out", request=None))
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert exc_info.value.code == WeatherProviderErrorCode.TIMEOUT
    assert exc_info.value.retryable is True


def test_connection_failure_maps_to_provider_unavailable_retryable():
    handler = _raising_handler(httpx.ConnectError("connection refused", request=None))
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert exc_info.value.code == WeatherProviderErrorCode.PROVIDER_UNAVAILABLE
    assert exc_info.value.retryable is True


def test_http_400_maps_to_invalid_request_not_retryable():
    handler = lambda r: httpx.Response(400, json={"error": True, "reason": "some provider text"})
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert exc_info.value.code == WeatherProviderErrorCode.INVALID_REQUEST
    assert exc_info.value.retryable is False


def test_http_401_maps_to_authentication_failed_not_retryable():
    handler = lambda r: httpx.Response(401, json={"error": True, "reason": "unauthorized"})
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert exc_info.value.code == WeatherProviderErrorCode.AUTHENTICATION_FAILED
    assert exc_info.value.retryable is False


def test_http_403_maps_to_unknown_provider_error_not_authentication():
    # V1 has no auth on the free endpoint, so 403 must not be assumed to be
    # an authentication failure (doc section 28).
    handler = lambda r: httpx.Response(403, json={"error": True, "reason": "blocked"})
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert exc_info.value.code == WeatherProviderErrorCode.UNKNOWN_PROVIDER_ERROR
    assert exc_info.value.retryable is False


def test_http_429_maps_to_rate_limited_retryable():
    handler = lambda r: httpx.Response(429, json={"error": True, "reason": "too many requests"})
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert exc_info.value.code == WeatherProviderErrorCode.RATE_LIMITED
    assert exc_info.value.retryable is True


@pytest.mark.parametrize("status", [500, 502, 503])
def test_http_5xx_maps_to_provider_unavailable_retryable(status):
    handler = lambda r: httpx.Response(status, json={"error": True, "reason": "server error"})
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert exc_info.value.code == WeatherProviderErrorCode.PROVIDER_UNAVAILABLE
    assert exc_info.value.retryable is True


def test_unexpected_status_maps_to_unknown_provider_error():
    handler = lambda r: httpx.Response(418, json={"error": True, "reason": "I'm a teapot"})
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert exc_info.value.code == WeatherProviderErrorCode.UNKNOWN_PROVIDER_ERROR


def test_provider_reason_never_appears_in_safe_message():
    secret_looking_reason = "internal-db-host-10.0.5.3 rejected geo query token ABCXYZ"
    handler = lambda r: httpx.Response(400, json={"error": True, "reason": secret_looking_reason})
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert secret_looking_reason not in exc_info.value.safe_message
    assert secret_looking_reason not in str(exc_info.value.public_fields())


def test_provider_reason_reachable_only_via_internal_cause():
    secret_looking_reason = "quota exceeded for internal-account-42"
    handler = lambda r: httpx.Response(400, json={"error": True, "reason": secret_looking_reason})
    with pytest.raises(WeatherProviderError) as exc_info:
        run_provider_call(handler, make_request())
    assert secret_looking_reason in str(exc_info.value.internal_cause)
