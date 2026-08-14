"""Endpoint-specific Sorgenia/Bidgely API methods."""

import json
from typing import Any

from custom_components.sorgenia.sorgenia_api import bidgely
from custom_components.sorgenia.sorgenia_api.auth.base import AbstractAuth
from custom_components.sorgenia.sorgenia_api.errors import ClientError, error_from_response, raise_for_api_response


class SorgeniaApi:
    """Consumption API, independent from how Sorgenia authentication works."""

    def __init__(
        self,
        auth: AbstractAuth,
        *,
        client_code: str,
        pod: str,
        bidgely_user_id: str,
        subscription_key: str,
        timeout: float = 30.0,
    ) -> None:
        """Initialize the consumption API with its authenticated account context."""
        self._auth = auth
        self._client_code = client_code
        self._pod = pod
        self._bidgely_user_id = bidgely_user_id
        self._subscription_key = subscription_key
        self._timeout = timeout

    async def async_get_bidgely_jwt(self) -> str:
        """Request the JWT that must be exchanged with Bidgely SSO."""
        response = await self._auth.async_request(
            "POST",
            "/extlogin/validate",
            headers={
                "Accept": "application/json",
                "Ocp-Apim-Subscription-Key": self._subscription_key,
            },
            json={"codiceCliente": self._client_code, "pod": self._pod},
            timeout=self._timeout,
        )
        async with response:
            raw = await response.read()
            payload = _decode_json(raw)
            if response.status >= 400:
                raise error_from_response(
                    payload,
                    http_status=response.status,
                    endpoint=str(response.url),
                    message="POST extlogin/validate failed",
                )
        raise_for_api_response(payload, endpoint="/extlogin/validate")
        token = payload.get("token") if isinstance(payload, dict) else None
        if not isinstance(token, str) or not token:
            raise ClientError("Sorgenia did not return a Bidgely JWT")
        return token

    async def async_get_usage_chart_details(self, **kwargs: Any) -> Any:
        """Return consumption details, including the required Bidgely SSO step."""
        bidgely_jwt = await self.async_get_bidgely_jwt()
        session = await bidgely.async_exchange_sso_token(
            self._auth.websession,
            bidgely_jwt,
            timeout=self._timeout,
        )
        return await bidgely.async_usage_chart_details(
            self._auth.websession,
            self._bidgely_user_id,
            session.access_token,
            timeout=self._timeout,
            **kwargs,
        )


def _decode_json(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError, json.JSONDecodeError:
        return {"errorDescription": raw.decode("utf-8", errors="replace")}
