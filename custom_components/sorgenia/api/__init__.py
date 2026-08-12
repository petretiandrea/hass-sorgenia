"""
API package for sorgenia.

Exception hierarchy:
    SorgeniaApiClientError (base)
    ├── SorgeniaApiClientCommunicationError (network/timeout)
    └── SorgeniaApiClientAuthenticationError (401/403)

The coordinator maps them onto ConfigEntryAuthFailed and UpdateFailed; nothing else
in the integration imports this package.
"""

from .client import (
    FAN_SPEEDS,
    SorgeniaApiClient,
    SorgeniaApiClientAuthenticationError,
    SorgeniaApiClientCommunicationError,
    SorgeniaApiClientError,
)

__all__ = [
    "FAN_SPEEDS",
    "SorgeniaApiClient",
    "SorgeniaApiClientAuthenticationError",
    "SorgeniaApiClientCommunicationError",
    "SorgeniaApiClientError",
]
