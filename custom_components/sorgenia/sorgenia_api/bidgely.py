"""Async client functions for the Bidgely SSO and consumption APIs."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import os
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse
from zoneinfo import ZoneInfo

from aiohttp import ClientSession, ClientTimeout

from custom_components.sorgenia.sorgenia_api.errors import BidgelyError
from custom_components.sorgenia.sorgenia_api.http import DEFAULT_TIMEOUT, async_request_json

BIDGELY_API = "https://api-read.eu.bidgely.com"
BIDGELY_SSO_URL = "https://ssoprod.bidgely.com/prod-eu/20013/sso/token"


@dataclass(frozen=True)
class BidgelySession:
    """Short-lived api-read bearer produced by the Bidgely SSO exchange."""

    access_token: str


async def async_exchange_sso_token(
    websession: ClientSession,
    bidgely_jwt: str,
    *,
    timeout: ClientTimeout | None = DEFAULT_TIMEOUT,
) -> BidgelySession:
    """Exchange the JWT returned by Sorgenia for the opaque Bidgely bearer."""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/json",
        "Authorization": f"Bearer {bidgely_jwt}",
        "User-Agent": os.getenv(
            "SORGENIA_USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36",
        ),
    }
    async with websession.get(
        BIDGELY_SSO_URL,
        headers=headers,
        timeout=timeout,
        allow_redirects=False,
    ) as response:
        location = response.headers.get("Location", "")
        body = await response.text()
        if response.status >= 400:
            raise BidgelyError(
                "Bidgely SSO exchange failed",
                http_status=response.status,
                description=body[:500],
                endpoint=BIDGELY_SSO_URL,
            )

    token = _token_from_location(location)
    if not token:
        raise BidgelyError(
            "Bidgely SSO did not return an api-read session token",
            http_status=response.status,
            endpoint=BIDGELY_SSO_URL,
            response={"location": location, "body": body[:500]},
        )
    return BidgelySession(access_token=token)


async def async_usage_chart_details(
    websession: ClientSession,
    user_id: str,
    bidgely_access_token: str,
    *,
    mode: str = "year",
    start: int | None = None,
    end: int | None = None,
    measurement_type: str = "ELECTRIC",
    locale: str = "it_IT",
    timeout: ClientTimeout | None = DEFAULT_TIMEOUT,
) -> Any:
    """Return the raw ``usage-chart-details`` document from Bidgely."""
    if start is None or end is None:
        month_start, month_end = _current_month_range()
        start = month_start if start is None else start
        end = month_end if end is None else end

    query = urlencode(
        {
            "measurement-type": measurement_type,
            "mode": mode,
            "start": start,
            "end": end,
            "date-format": "DATE_TIME",
            "locale": locale,
            "next-bill-cycle": "false",
            "show-at-granularity": "false",
            "skip-ongoing-cycle": "false",
        }
    )
    return await async_request_json(
        websession,
        "GET",
        f"{BIDGELY_API}/v2.0/dashboard/users/{user_id}/usage-chart-details?{query}",
        headers={
            "Authorization": f"Bearer {bidgely_access_token}",
            "X-Bidgely-Client-Type": os.getenv("BIDGELY_CLIENT_TYPE", "WEB"),
            "X-Bidgely-Pilot-Id": os.getenv("BIDGELY_PILOT_ID", "20013"),
            "Referer": "https://api-read.eu.bidgely.com/proxy.html",
        },
        timeout=timeout,
    )


def _current_month_range() -> tuple[int, int]:
    """Return inclusive Unix timestamps for the current Italian calendar month."""
    now = datetime.now(ZoneInfo("Europe/Rome"))
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    return int(month_start.timestamp()), int((next_month - timedelta(seconds=1)).timestamp())


def _token_from_location(location: str) -> str | None:
    values = parse_qs(urlparse(location).query)
    token = values.get("token", [None])[0]
    return token if isinstance(token, str) and token else None
