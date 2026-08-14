"""Constants for sorgenia."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "sorgenia"
ATTRIBUTION = "Data provided by Sorgenia."

CONF_ACCESS_TOKEN = "access_token"
CONF_CLIENT_CODE = "client_code"
CONF_OTP = "otp"
CONF_POD = "pod"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_VALIDATED_PHONE = "validated_phone"

CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"

DEFAULT_UPDATE_INTERVAL_HOURS = 24.0

***REMOVED***

SORGENIA_BASIC_AUTH = ""
SORGENIA_SUBSCRIPTION_KEY = ""
