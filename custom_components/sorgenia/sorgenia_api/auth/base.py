"""Home Assistant-style authentication abstraction."""

from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urljoin

from aiohttp import ClientResponse, ClientSession


class AbstractAuth(ABC):
    """Acquire a valid token and make authenticated HTTP requests.

    Request payloads and endpoint-specific behaviour belong to API classes,
    not here. Token persistence deliberately belongs to the caller.
    """

    def __init__(self, websession: ClientSession, host: str) -> None:
        """Initialize the shared HTTP session and API host."""
        self.websession = websession
        self.host = host.rstrip("/")

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid Sorgenia access token."""

    async def async_request(self, method: str, path_or_url: str, **kwargs: Any) -> ClientResponse:
        """Make an authenticated request without knowing its contents."""
        headers = dict(kwargs.pop("headers", {}))
        access_token = await self.async_get_access_token()
        headers["Authorization"] = f"Bearer {access_token}"
        url = (
            path_or_url
            if path_or_url.startswith(("https://", "http://"))
            else urljoin(f"{self.host}/", path_or_url.lstrip("/"))
        )
        return await self.websession.request(method, url, headers=headers, **kwargs)
