"""Asynchronous Sorgenia and Bidgely consumption API client."""

from custom_components.sorgenia.sorgenia_api.api import SorgeniaApi
from custom_components.sorgenia.sorgenia_api.auth import AbstractAuth, SorgeniaAuth, SorgeniaStaticAuth
from custom_components.sorgenia.sorgenia_api.error_codes import API_ERROR_CODES, ApiErrorInfo, describe_error
from custom_components.sorgenia.sorgenia_api.errors import (
    AuthenticationError,
    BidgelyError,
    ClientError,
    OtpError,
    OtpRequired,
    OtpValidationError,
    SorgeniaApiError,
)
from custom_components.sorgenia.sorgenia_api.models import SorgeniaTokens

__all__ = [
    "API_ERROR_CODES",
    "AbstractAuth",
    "ApiErrorInfo",
    "AuthenticationError",
    "BidgelyError",
    "ClientError",
    "OtpError",
    "OtpRequired",
    "OtpValidationError",
    "SorgeniaApi",
    "SorgeniaApiError",
    "SorgeniaAuth",
    "SorgeniaStaticAuth",
    "SorgeniaTokens",
    "describe_error",
]
