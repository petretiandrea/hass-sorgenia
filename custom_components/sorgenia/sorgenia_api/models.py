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


@dataclass(frozen=True)
class SorgeniaUsageInterval:
    """Consumption and cost for one interval returned by Bidgely."""

    interval_start: int
    interval_end: int
    consumption: float
    cost: float
    estimated_consumption: float | None
    is_ongoing: bool

    @classmethod
    def from_response(cls, response: Mapping[str, Any]) -> SorgeniaUsageInterval:
        """Create an interval from a Bidgely usage-chart item."""
        interval_start = _as_int(response.get("intervalStart"))
        interval_end = _as_int(response.get("intervalEnd"))
        consumption = _as_float(response.get("consumption"))
        cost = _as_float(response.get("cost"))
        if interval_start is None or interval_end is None or consumption is None or cost is None:
            raise ValueError("usage interval is missing a required numeric value")
        return cls(
            interval_start=interval_start,
            interval_end=interval_end,
            consumption=consumption,
            cost=cost,
            estimated_consumption=_as_float(response.get("estimatedConsumption")),
            is_ongoing=response.get("isOngoingInterval") is True,
        )


@dataclass(frozen=True)
class SorgeniaUsageChartDetails:
    """The consumption intervals returned by Bidgely usage-chart-details."""

    intervals: tuple[SorgeniaUsageInterval, ...]

    @classmethod
    def from_response(cls, response: Mapping[str, Any]) -> SorgeniaUsageChartDetails:
        """Create typed chart details from a Bidgely API response."""
        payload = response.get("payload")
        if not isinstance(payload, Mapping):
            raise TypeError("usage-chart-details response does not contain payload")
        interval_data = payload.get("usageChartDataList")
        if not isinstance(interval_data, list):
            raise TypeError("usage-chart-details response does not contain usageChartDataList")
        intervals: list[SorgeniaUsageInterval] = []
        for item in interval_data:
            if not isinstance(item, Mapping):
                continue
            try:
                intervals.append(SorgeniaUsageInterval.from_response(item))
            except ValueError:
                continue
        if not intervals:
            raise ValueError("usage-chart-details response contains no usage intervals")
        return cls(intervals=tuple(intervals))

    @property
    def ongoing_interval(self) -> SorgeniaUsageInterval | None:
        """Return the current billing interval, when present."""
        return next((interval for interval in self.intervals if interval.is_ongoing), None)


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            numeric_value = float(value)
        except ValueError:
            return None
        return int(numeric_value) if numeric_value.is_integer() else None
    return None
