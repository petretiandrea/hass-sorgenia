"""Sorgenia credential and OTP validation for the config flow."""

from typing import TYPE_CHECKING

from custom_components.sorgenia.const import SORGENIA_BASIC_AUTH, SORGENIA_SUBSCRIPTION_KEY
from custom_components.sorgenia.sorgenia_api import SorgeniaApi, SorgeniaAuth, SorgeniaTokens
from homeassistant.helpers.aiohttp_client import async_get_clientsession

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def async_login(hass: HomeAssistant, username: str, password: str) -> SorgeniaTokens:
    """Log in with username and password, returning the issued tokens."""
    auth = _create_auth(hass)
    return await auth.async_login(username, password)


async def async_send_otp(hass: HomeAssistant, username: str, phone: str) -> None:
    """Send an OTP to the phone confirmed by Sorgenia."""
    auth = _create_auth(hass)
    await auth.async_send_otp(username, phone)


async def async_verify_otp(
    hass: HomeAssistant,
    username: str,
    phone: str,
    otp: str,
    otp_token: str,
) -> SorgeniaTokens:
    """Verify an OTP and return the issued tokens."""
    auth = _create_auth(hass)
    return await auth.async_verify_otp(username, phone, otp, otp_token)


async def async_validate_tokens(
    hass: HomeAssistant,
    username: str,
    client_code: str,
    pod: str,
    access_token: str,
    refresh_token: str,
) -> SorgeniaTokens:
    """Validate existing tokens without using the OTP login endpoints."""
    auth = SorgeniaAuth(
        async_get_clientsession(hass),
        subscription_key=SORGENIA_SUBSCRIPTION_KEY,
        basic_auth=SORGENIA_BASIC_AUTH,
        tokens=SorgeniaTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            username=username,
        ),
    )
    client = SorgeniaApi(
        auth,
        client_code=client_code,
        pod=pod,
        subscription_key=SORGENIA_SUBSCRIPTION_KEY,
    )
    await client.async_get_bidgely_jwt()
    assert auth.tokens is not None
    return auth.tokens


def _create_auth(hass: HomeAssistant) -> SorgeniaAuth:
    """Create an authentication client backed by Home Assistant's shared session."""
    return SorgeniaAuth(
        async_get_clientsession(hass),
        subscription_key=SORGENIA_SUBSCRIPTION_KEY,
        basic_auth=SORGENIA_BASIC_AUTH,
    )


__all__ = ["async_login", "async_send_otp", "async_validate_tokens", "async_verify_otp"]
