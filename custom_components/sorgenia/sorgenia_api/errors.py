"""Exceptions raised by the Sorgenia and Bidgely API clients."""

import re
from typing import Any

from custom_components.sorgenia.sorgenia_api.error_codes import describe_error


class SorgeniaApiError(RuntimeError):
    """Base exception raised when a Sorgenia API request cannot be completed."""


class SorgeniaApiCommunicationError(SorgeniaApiError):
    """Network, DNS, timeout, or transport error communicating with Sorgenia."""


class SorgeniaApiResponseError(SorgeniaApiError):
    """Structured error returned by Sorgenia or Bidgely."""

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        http_status: int | None = None,
        description: str | None = None,
        error_copy: str | None = None,
        response: Any = None,
        endpoint: str | None = None,
    ) -> None:
        """Initialize a structured error with the API response details."""
        self.error_code = str(error_code) if error_code is not None else None
        self.http_status = http_status
        self.description = description
        self.error_copy = error_copy
        self.response = response
        self.endpoint = endpoint
        self.info = describe_error(self.error_code)
        super().__init__(message)

    @property
    def known(self) -> bool:
        """Return whether the error code exists in the local catalogue."""
        return self.info is not None

    @property
    def error_name(self) -> str | None:
        """Return the symbolic name for a known error code."""
        return self.info.name if self.info else None

    def __str__(self) -> str:
        """Return a redacted, human-readable error message."""
        status = f"HTTP {self.http_status}" if self.http_status else "API error"
        code = f" [{self.error_code}]" if self.error_code else ""
        text = self.description or self.error_copy or self.args[0]
        return f"{status}{code}: {_redact(text)}"


class SorgeniaApiAuthenticationError(SorgeniaApiResponseError):
    """Authentication, credentials, or token error."""


class OtpError(SorgeniaApiAuthenticationError):
    """OTP sending or validation error."""


class OtpValidationError(OtpError):
    """The submitted OTP is invalid, stale, or attempts are exhausted."""


class BidgelyError(SorgeniaApiResponseError):
    """Error returned by the consumption API."""


class OtpRequired(SorgeniaApiAuthenticationError):
    """Login accepted the credentials but requires phone OTP validation."""

    def __init__(
        self,
        message: str,
        *,
        token: str,
        validated_phone: str | None,
        response: object,
    ) -> None:
        """Initialize the OTP challenge returned by a successful login."""
        self.token = token
        self.validated_phone = validated_phone
        self.response = response
        super().__init__(
            message,
            error_code="1192",
            description=message,
            response=response,
            endpoint="/sorgenia/V5/login",
        )


def error_from_response(
    response: Any,
    *,
    http_status: int | None = None,
    endpoint: str | None = None,
    message: str | None = None,
) -> SorgeniaApiResponseError:
    """Build the appropriate exception from a JSON error payload."""
    if isinstance(response, dict):
        code = response.get("errorCode") or response.get("code") or response.get("error")
        description = response.get("errorDescription") or response.get("error_description")
        error_copy = response.get("errorCopy")
    else:
        code = None
        description = None
        error_copy = None

    cls: type[SorgeniaApiResponseError] = SorgeniaApiResponseError
    if str(code) in {"1177", "1187", "1189"}:
        cls = OtpValidationError
    elif str(code) in {"1182", "1183", "1184", "1185", "1186", "1188"}:
        cls = OtpError
    elif str(code) in {"001", "002", "009", "010", "1004", "1015", "1180", "1191", "1192"}:
        cls = SorgeniaApiAuthenticationError
    elif str(code) == "invalid_token":
        cls = BidgelyError

    return cls(
        message or description or error_copy or "API request failed",
        error_code=str(code) if code is not None else None,
        http_status=http_status,
        description=description,
        error_copy=error_copy,
        response=response,
        endpoint=endpoint,
    )


def raise_for_api_response(response: Any, *, endpoint: str) -> None:
    """Raise for Sorgenia's application-level ``status=KO`` responses."""
    if isinstance(response, dict) and str(response.get("status", "")).upper() == "KO":
        raise error_from_response(response, endpoint=endpoint)


def _redact(value: str) -> str:
    # Bidgely includes the complete JWT in invalid_token descriptions.
    return re.sub(r"(Invalid access token:\s+)[^\s]+", r"\1<redacted>", str(value))
