"""Static-token authentication for standalone scripts and tests."""

from aiohttp import ClientSession

from custom_components.sorgenia.sorgenia_api.auth.base import AbstractAuth
from custom_components.sorgenia.sorgenia_api.auth.sorgenia import SORGENIA_API


class SorgeniaStaticAuth(AbstractAuth):
    """Concrete ``AbstractAuth`` backed by a static Sorgenia access token.

    Useful when the caller, for example a Home Assistant integration, owns the
    token lifecycle and only needs this library to make API requests.
    """

    def __init__(
        self,
        websession: ClientSession,
        endpoint: str,
        access_token: str,
    ) -> None:
        """Initialize authentication with a caller-managed access token."""
        super().__init__(websession, endpoint or SORGENIA_API)
        self._access_token = access_token

    async def async_get_access_token(self) -> str:
        """Return the access token supplied by the caller."""
        return self._access_token
