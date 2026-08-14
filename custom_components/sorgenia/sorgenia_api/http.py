"""Small asynchronous HTTP primitives shared by the library."""

import json
import os
from typing import Any

from aiohttp import ClientError as AiohttpClientError, ClientSession, ClientTimeout

from custom_components.sorgenia.sorgenia_api.errors import ClientError, error_from_response

DEFAULT_TIMEOUT = ClientTimeout(total=30)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


async def async_request_json(
    session: ClientSession,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    timeout: ClientTimeout | None = DEFAULT_TIMEOUT,
    allow_redirects: bool = True,
) -> Any:
    """Perform an async JSON request and convert API errors to library errors."""
    request_headers = dict(headers or {})
    request_headers.setdefault("User-Agent", os.getenv("SORGENIA_USER_AGENT", DEFAULT_USER_AGENT))
    request_headers.setdefault("Accept", "application/json")

    try:
        async with session.request(
            method,
            url,
            headers=request_headers,
            json=json_body,
            timeout=timeout,
            allow_redirects=allow_redirects,
        ) as response:
            raw = await response.read()
            payload = _decode_json(raw)
            if response.status >= 400:
                raise error_from_response(
                    payload,
                    http_status=response.status,
                    endpoint=str(response.url),
                    message=f"{method} {url} failed",
                )
            return payload
    except AiohttpClientError as exc:
        raise ClientError(f"network error calling {url}: {exc}") from exc


def _decode_json(raw: bytes) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError, json.JSONDecodeError:
        return {"errorDescription": raw.decode("utf-8", errors="replace")}
