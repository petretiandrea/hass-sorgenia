"""Constants for sorgenia."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "sorgenia"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

CONF_ACCESS_TOKEN = "access_token"
CONF_OTP = "otp"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_VALIDATED_PHONE = "validated_phone"

CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"

DEFAULT_UPDATE_INTERVAL_HOURS = 1.0

SORGENIA_BASIC_AUTH = ""
SORGENIA_SUBSCRIPTION_KEY = ""
