"""Config flow schemas for the user, reconfigure and reauth steps."""

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from custom_components.sorgenia.const import CONF_ACCESS_TOKEN, CONF_CLIENT_CODE, CONF_OTP, CONF_POD, CONF_REFRESH_TOKEN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector

_USERNAME_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(
        type=selector.TextSelectorType.TEXT,
        autocomplete="username",
    ),
)
_PASSWORD_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(
        type=selector.TextSelectorType.PASSWORD,
        autocomplete="current-password",
    ),
)
_OTP_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(
        type=selector.TextSelectorType.TEXT,
        autocomplete="one-time-code",
    ),
)
_TOKEN_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(
        type=selector.TextSelectorType.PASSWORD,
    ),
)


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Build the schema for the user step.

    Args:
        defaults: Previously submitted values, used to pre-fill the form.

    Returns:
        The voluptuous schema for the credentials form.

    """
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_USERNAME,
                default=defaults.get(CONF_USERNAME, vol.UNDEFINED),
            ): _USERNAME_SELECTOR,
            vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
            vol.Required(CONF_CLIENT_CODE): _USERNAME_SELECTOR,
            vol.Required(CONF_POD): _USERNAME_SELECTOR,
        },
    )


def get_tokens_schema() -> vol.Schema:
    """Build the schema for setup with existing session tokens."""
    return vol.Schema(
        {
            vol.Required(CONF_USERNAME): _USERNAME_SELECTOR,
            vol.Required(CONF_CLIENT_CODE): _USERNAME_SELECTOR,
            vol.Required(CONF_POD): _USERNAME_SELECTOR,
            vol.Required(CONF_ACCESS_TOKEN): _TOKEN_SELECTOR,
            vol.Required(CONF_REFRESH_TOKEN): _TOKEN_SELECTOR,
        },
    )


def get_reconfigure_schema(username: str) -> vol.Schema:
    """
    Build the schema for the reconfigure step.

    Args:
        username: The entry's current username, used to pre-fill the form.

    Returns:
        The voluptuous schema for the reconfigure form.

    """
    return vol.Schema(
        {
            vol.Required(CONF_USERNAME, default=username): _USERNAME_SELECTOR,
            vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
        },
    )


def get_reauth_schema(username: str) -> vol.Schema:
    """
    Build the schema for the reauth step.

    Args:
        username: The entry's current username, used to pre-fill the form.

    Returns:
        The voluptuous schema for the reauth form.

    """
    return vol.Schema(
        {
            vol.Required(CONF_USERNAME, default=username): _USERNAME_SELECTOR,
            vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
        },
    )


def get_otp_schema() -> vol.Schema:
    """Build the schema for the OTP verification step."""
    return vol.Schema({vol.Required(CONF_OTP): _OTP_SELECTOR})


__all__ = [
    "get_otp_schema",
    "get_reauth_schema",
    "get_reconfigure_schema",
    "get_tokens_schema",
    "get_user_schema",
]
