"""Asynchronous Sorgenia and Bidgely consumption API client."""

from custom_components.sorgenia.sorgenia_api.api import SorgeniaApi
from custom_components.sorgenia.sorgenia_api.auth import AbstractAuth, SorgeniaAuth, SorgeniaStaticAuth
from custom_components.sorgenia.sorgenia_api.error_codes import API_ERROR_CODES, ApiErrorInfo, describe_error
from custom_components.sorgenia.sorgenia_api.errors import (
    BidgelyError,
    OtpError,
    OtpRequired,
    OtpValidationError,
    SorgeniaApiAuthenticationError,
    SorgeniaApiCommunicationError,
    SorgeniaApiError,
    SorgeniaApiResponseError,
)
from custom_components.sorgenia.sorgenia_api.models import (
    SorgeniaTokens,
    SorgeniaUsageChartDetails,
    SorgeniaUsageInterval,
)

__all__ = [
    "API_ERROR_CODES",
    "AbstractAuth",
    "ApiErrorInfo",
    "BidgelyError",
    "OtpError",
    "OtpRequired",
    "OtpValidationError",
    "SorgeniaApi",
    "SorgeniaApiAuthenticationError",
    "SorgeniaApiCommunicationError",
    "SorgeniaApiError",
    "SorgeniaApiResponseError",
    "SorgeniaAuth",
    "SorgeniaStaticAuth",
    "SorgeniaTokens",
    "SorgeniaUsageChartDetails",
    "SorgeniaUsageInterval",
    "describe_error",
]
