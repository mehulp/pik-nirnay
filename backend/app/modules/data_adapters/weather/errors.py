"""B1 — normalized, provider-neutral weather errors.

Authoritative source: docs/data/b1-weather-provider-contract.md, sections
21-22.

`retryable` is always supplied by the raiser (adapter or capability
validator), never derived from `code` alone — the same error code can have
different retry semantics across providers (section 22).
"""

from __future__ import annotations

from enum import Enum


class WeatherProviderErrorCode(str, Enum):
    INVALID_REQUEST = "INVALID_REQUEST"
    UNSUPPORTED_VARIABLE = "UNSUPPORTED_VARIABLE"
    UNSUPPORTED_RANGE = "UNSUPPORTED_RANGE"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    MALFORMED_RESPONSE = "MALFORMED_RESPONSE"
    UNKNOWN_PROVIDER_ERROR = "UNKNOWN_PROVIDER_ERROR"


class WeatherProviderError(Exception):
    """Normalized weather-provider error (section 21).

    `internal_cause` (an underlying exception, raw provider payload, etc.)
    is intentionally excluded from `public_fields()` — the only method
    meant to back a serialized/farmer-facing representation. Use
    `raise WeatherProviderError(...) from original_exc` for standard Python
    exception chaining when you also want `internal_cause` populated.
    """

    def __init__(
        self,
        *,
        code: WeatherProviderErrorCode,
        provider_id: str,
        retryable: bool,
        safe_message: str,
        internal_cause: BaseException | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.provider_id = provider_id
        self.retryable = retryable
        self.safe_message = safe_message
        self.internal_cause = internal_cause

    def public_fields(self) -> dict[str, object]:
        """The only fields safe to serialize or show to an end user."""
        return {
            "code": self.code.value,
            "provider_id": self.provider_id,
            "retryable": self.retryable,
            "safe_message": self.safe_message,
        }
