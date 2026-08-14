"""JSON-serializable public models."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SorgeniaTokens:
    """Sorgenia session tokens.

    The token data is intentionally serializable but persistence is left to
    the application using this library, as recommended by Home Assistant.
    """

    access_token: str
    refresh_token: str | None = None
    username: str | None = None
    validated_phone: str | None = None

    @classmethod
    def from_response(cls, response: Mapping[str, Any]) -> SorgeniaTokens:
        """Create tokens from a Sorgenia API response."""
        access_token = response.get("accessToken")
        if not isinstance(access_token, str) or not access_token:
            raise ValueError("response does not contain accessToken")
        return cls(
            access_token=access_token,
            refresh_token=_as_str(response.get("refreshToken")),
            username=_as_str(response.get("username")),
            validated_phone=_as_str(response.get("validatedPhone")),
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SorgeniaTokens:
        """Create tokens from persisted JSON-compatible data."""
        return cls.from_response(data)

    def as_dict(self) -> dict[str, str]:
        """Return tokens as JSON-compatible data for persistence."""
        data = {"accessToken": self.access_token}
        if self.refresh_token:
            data["refreshToken"] = self.refresh_token
        if self.username:
            data["username"] = self.username
        if self.validated_phone:
            data["validatedPhone"] = self.validated_phone
        return data


def _as_str(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None
