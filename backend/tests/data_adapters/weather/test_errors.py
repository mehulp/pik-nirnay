"""B1 tests: normalized WeatherProviderError.

Per docs/data/b1-weather-provider-contract.md section 32, item 25, and
sections 21-22.
"""

from app.modules.data_adapters.weather.errors import WeatherProviderError, WeatherProviderErrorCode


def test_all_normalized_error_codes_exist():
    expected = {
        "INVALID_REQUEST",
        "UNSUPPORTED_VARIABLE",
        "UNSUPPORTED_RANGE",
        "DATA_UNAVAILABLE",
        "PROVIDER_UNAVAILABLE",
        "RATE_LIMITED",
        "TIMEOUT",
        "AUTHENTICATION_FAILED",
        "MALFORMED_RESPONSE",
        "UNKNOWN_PROVIDER_ERROR",
    }
    assert {member.value for member in WeatherProviderErrorCode} == expected


def test_error_carries_normalized_fields():
    error = WeatherProviderError(
        code=WeatherProviderErrorCode.TIMEOUT,
        provider_id="open_meteo",
        retryable=True,
        safe_message="The weather provider timed out.",
    )
    assert error.code == WeatherProviderErrorCode.TIMEOUT
    assert error.provider_id == "open_meteo"
    assert error.retryable is True
    assert error.safe_message == "The weather provider timed out."


def test_public_fields_excludes_internal_cause():
    original = RuntimeError("connection reset by peer at 10.0.0.5:443 with secret-looking token XYZ")
    error = WeatherProviderError(
        code=WeatherProviderErrorCode.PROVIDER_UNAVAILABLE,
        provider_id="open_meteo",
        retryable=True,
        safe_message="The weather provider is temporarily unavailable.",
        internal_cause=original,
    )
    public = error.public_fields()
    assert set(public.keys()) == {"code", "provider_id", "retryable", "safe_message"}
    assert "internal_cause" not in public
    assert "10.0.0.5" not in str(public)
    assert error.internal_cause is original  # still reachable for developer/logging use


def test_str_of_error_is_safe_message_only():
    error = WeatherProviderError(
        code=WeatherProviderErrorCode.MALFORMED_RESPONSE,
        provider_id="open_meteo",
        retryable=False,
        safe_message="The provider returned an unexpected response.",
        internal_cause=ValueError("raw json parse failure: line 4 col 17"),
    )
    assert str(error) == "The provider returned an unexpected response."
    assert "col 17" not in str(error)


def test_same_error_code_can_have_different_retryability():
    # B1 does not assume a fixed retryability per code (section 22): the
    # raiser supplies it, and it may legitimately differ by situation.
    retryable = WeatherProviderError(
        code=WeatherProviderErrorCode.DATA_UNAVAILABLE,
        provider_id="open_meteo",
        retryable=True,
        safe_message="Data temporarily unavailable.",
    )
    not_retryable = WeatherProviderError(
        code=WeatherProviderErrorCode.DATA_UNAVAILABLE,
        provider_id="open_meteo",
        retryable=False,
        safe_message="Data unavailable for this location.",
    )
    assert retryable.code == not_retryable.code
    assert retryable.retryable != not_retryable.retryable


def test_exception_chaining_still_works_via_raise_from():
    original = ValueError("boom")
    try:
        try:
            raise original
        except ValueError as exc:
            raise WeatherProviderError(
                code=WeatherProviderErrorCode.UNKNOWN_PROVIDER_ERROR,
                provider_id="open_meteo",
                retryable=False,
                safe_message="An unexpected error occurred.",
            ) from exc
    except WeatherProviderError as error:
        assert error.__cause__ is original
