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

BIDGELY_USER_ID = "5c347a40-6905-4fbd-ad8c-bddc1e7ea4dd"

SORGENIA_BASIC_AUTH = ""
SORGENIA_SUBSCRIPTION_KEY = ""
