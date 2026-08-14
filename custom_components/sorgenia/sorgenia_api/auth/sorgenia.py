"""Sorgenia credential acquisition, OTP and refresh-token flow."""

import base64
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import replace
import hashlib
import json
import time
from typing import Any

from aiohttp import ClientSession, ClientTimeout

from custom_components.sorgenia.sorgenia_api.auth.base import AbstractAuth
from custom_components.sorgenia.sorgenia_api.errors import (
    OtpRequired,
    SorgeniaApiAuthenticationError,
    SorgeniaApiError,
    raise_for_api_response,
)
from custom_components.sorgenia.sorgenia_api.http import DEFAULT_TIMEOUT, async_request_json
from custom_components.sorgenia.sorgenia_api.models import SorgeniaTokens

SORGENIA_API = "https://api-prod.sorgenia.it"


class SorgeniaAuth(AbstractAuth):
    """Acquire and refresh Sorgenia tokens; does not persist them."""

    def __init__(
        self,
        websession: ClientSession,
        *,
        subscription_key: str,
        basic_auth: str,
        tokens: SorgeniaTokens | None = None,
        timeout: ClientTimeout | None = DEFAULT_TIMEOUT,
        host: str = SORGENIA_API,
        token_updated: Callable[[SorgeniaTokens], Awaitable[None]] | None = None,
    ) -> None:
        """Initialize authentication with the Sorgenia application credentials."""
        super().__init__(websession, host)
        self.subscription_key = subscription_key
        self.basic_auth = basic_auth
        self.timeout = timeout
        self._tokens = tokens
        self._token_updated = token_updated

    @property
    def tokens(self) -> SorgeniaTokens | None:
        """Current in-memory tokens, suitable for serialization by callers."""
        return self._tokens

    def set_tokens(self, tokens: SorgeniaTokens) -> None:
        """Replace in-memory tokens restored by the caller."""
        self._tokens = tokens

    async def async_get_access_token(self) -> str:
        """Return a valid access token, refreshing it when necessary."""
        if self._tokens and self._tokens.access_token and not _is_expiring(self._tokens.access_token):
            return self._tokens.access_token
        if self._tokens and self._tokens.refresh_token and self._tokens.username:
            tokens = await self.async_refresh()
            return tokens.access_token
        if self._tokens and self._tokens.access_token:
            raise SorgeniaApiAuthenticationError("Sorgenia access token is expired and cannot be refreshed")
        raise SorgeniaApiAuthenticationError("No Sorgenia access token is available")

    async def async_login(self, username: str, password: str) -> SorgeniaTokens:
        """Log in with credentials and return the resulting token pair."""
        response = await async_request_json(
            self.websession,
            "POST",
            f"{self.host}/sorgenia/V5/login",
            headers=self._basic_headers(),
            json_body={
                "username": username.strip(),
                "password": hashlib.sha256(password.encode("utf-8")).hexdigest(),
                "sourceChannel": "MYS",
            },
            timeout=self.timeout,
        )
        if isinstance(response, dict) and response.get("errorCode") == "1192":
            token = response.get("accessToken")
            if isinstance(token, str) and token:
                raise OtpRequired(
                    "Sorgenia richiede la verifica OTP del telefono",
                    token=token,
                    validated_phone=response.get("validatedPhone"),
                    response=response,
                )
        tokens = _tokens_from_response(response, f"{self.host}/sorgenia/V5/login")
        await self._async_set_tokens(tokens)
        return tokens

    async def async_send_otp(
        self,
        username: str,
        phone: str,
        *,
        dialing_code: str | None = None,
        phone_type: str = "VALIDATED",
    ) -> Mapping[str, Any]:
        """Send an OTP to the selected phone number."""
        response = await async_request_json(
            self.websession,
            "POST",
            f"{self.host}/sorgenia/V2/sendOTP",
            headers=self._basic_headers(),
            json_body={
                "username": username.strip(),
                "phone": phone,
                "phoneType": phone_type,
                "sourceChannel": "MYS",
                **({"dialingCode": dialing_code} if dialing_code else {}),
            },
            timeout=self.timeout,
        )
        raise_for_api_response(response, endpoint=f"{self.host}/sorgenia/V2/sendOTP")
        return _mapping_response(response)

    async def async_verify_otp(
        self,
        username: str,
        phone: str,
        otp: str,
        otp_token: str,
        *,
        dialing_code: str | None = None,
        phone_type: str = "VALIDATED",
    ) -> SorgeniaTokens:
        """Verify an OTP and return the resulting token pair."""
        response = await async_request_json(
            self.websession,
            "POST",
            f"{self.host}/sorgenia/V2/verifyOTP",
            headers={
                "Authorization": f"Bearer {otp_token}",
                "Ocp-Apim-Subscription-Key": self.subscription_key,
            },
            json_body={
                "username": username.strip(),
                "phone": phone,
                "otp": otp,
                "phoneType": phone_type,
                "sourceChannel": "MYS",
                **({"dialingCode": dialing_code} if dialing_code else {}),
            },
            timeout=self.timeout,
        )
        tokens = _tokens_from_response(response, f"{self.host}/sorgenia/V2/verifyOTP")
        await self._async_set_tokens(tokens)
        return tokens

    async def async_refresh(self) -> SorgeniaTokens:
        """Rotate the refresh token and return the new token pair."""
        if not self._tokens or not self._tokens.refresh_token or not self._tokens.username:
            raise SorgeniaApiAuthenticationError("A username and refresh token are required")
        response = await async_request_json(
            self.websession,
            "POST",
            f"{self.host}/sorgenia/V6/refreshtoken",
            headers={
                **self._basic_headers(),
                "refreshToken": self._tokens.refresh_token,
            },
            json_body={"username": self._tokens.username, "sourceChannel": "MYS"},
            timeout=self.timeout,
        )
        tokens = _tokens_from_response(response, f"{self.host}/sorgenia/V6/refreshtoken")
        await self._async_set_tokens(tokens)
        return tokens

    async def _async_set_tokens(self, tokens: SorgeniaTokens) -> None:
        """Store new tokens and notify the application that persists them."""
        if self._tokens is not None:
            tokens = replace(
                tokens,
                username=tokens.username or self._tokens.username,
                validated_phone=tokens.validated_phone or self._tokens.validated_phone,
            )
        self._tokens = tokens
        if self._token_updated is not None:
            await self._token_updated(tokens)

    def _basic_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Basic {self.basic_auth}",
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }


def _tokens_from_response(response: Any, endpoint: str) -> SorgeniaTokens:
    raise_for_api_response(response, endpoint=endpoint)
    if not isinstance(response, Mapping):
        raise SorgeniaApiError(f"{endpoint} returned a non-object response")
    try:
        return SorgeniaTokens.from_response(response)
    except ValueError as exc:
        raise SorgeniaApiError(f"{endpoint} did not return an access token") from exc


def _mapping_response(response: Any) -> Mapping[str, Any]:
    if not isinstance(response, Mapping):
        raise SorgeniaApiError("Sorgenia returned a non-object response")
    return response


def _is_expiring(token: str, *, leeway: int = 60) -> bool:
    """Return whether a JWT is expired or will expire shortly.

    Non-JWT values are accepted; their validity can only be determined by the
    remote API, which is appropriate for opaque tokens.
    """
    parts = token.split(".")
    if len(parts) != 3:
        return False
    try:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        expires_at = json.loads(base64.urlsafe_b64decode(payload)).get("exp")
        return isinstance(expires_at, (int, float)) and expires_at <= time.time() + leeway
    except ValueError, UnicodeDecodeError, json.JSONDecodeError:
        return False
