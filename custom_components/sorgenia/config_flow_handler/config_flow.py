"""Config flow for Sorgenia authentication, OTP and token persistence."""

from typing import Any

from custom_components.sorgenia.const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_CODE,
    CONF_OTP,
    CONF_REFRESH_TOKEN,
    CONF_VALIDATED_PHONE,
    DOMAIN,
    LOGGER,
)
from custom_components.sorgenia.sorgenia_api import (
    OtpRequired,
    OtpValidationError,
    SorgeniaApiAuthenticationError,
    SorgeniaApiCommunicationError,
    SorgeniaApiError,
    SorgeniaTokens,
)
from homeassistant import config_entries
from homeassistant.config_entries import SOURCE_REAUTH, SOURCE_RECONFIGURE
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.loader import async_get_loaded_integration

from .options_flow import SorgeniaOptionsFlow
from .schemas import get_otp_schema, get_reauth_schema, get_reconfigure_schema, get_user_schema
from .validators import async_login, async_send_otp, async_verify_otp


class SorgeniaConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Sorgenia credential and OTP flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the temporary state used between credential and OTP steps."""
        self._pending_credentials: dict[str, Any] | None = None
        self._otp_phone: str | None = None
        self._otp_token: str | None = None

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SorgeniaOptionsFlow:
        """Return the options flow for this handler."""
        return SorgeniaOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow started by the user."""
        if user_input is not None:
            return await self._async_submit_credentials(user_input, "user")

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(),
            description_placeholders={"documentation_url": integration.documentation or ""},
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration of an existing entry."""
        if self.source != SOURCE_RECONFIGURE:
            return self.async_abort(reason="unknown")

        entry = self._get_reconfigure_entry()
        if user_input is not None:
            return await self._async_submit_credentials(user_input, "reconfigure")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                get_reconfigure_schema(entry.data.get(CONF_USERNAME, "")), entry.data
            ),
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any],
    ) -> config_entries.ConfigFlowResult:
        """Start reauthentication after an authentication failure."""
        if self.source != SOURCE_REAUTH:
            return self.async_abort(reason="unknown")
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Collect replacement credentials for reauthentication."""
        entry = self._get_reauth_entry()
        if user_input is not None:
            return await self._async_submit_credentials(user_input, "reauth")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=get_reauth_schema(entry.data.get(CONF_USERNAME, "")),
            description_placeholders={"name": entry.title},
        )

    async def async_step_otp(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Verify the one-time password sent by Sorgenia."""
        if not self._pending_credentials or not self._otp_phone or not self._otp_token:
            return self.async_abort(reason="otp_session_expired")

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                tokens = await async_verify_otp(
                    self.hass,
                    self._pending_credentials[CONF_USERNAME],
                    self._otp_phone,
                    user_input[CONF_OTP],
                    self._otp_token,
                )
            except OtpValidationError:
                errors["base"] = "invalid_otp"
            except SorgeniaApiAuthenticationError:
                errors["base"] = "invalid_otp"
            except SorgeniaApiCommunicationError:
                errors["base"] = "cannot_connect"
            except SorgeniaApiError:
                LOGGER.exception("Unexpected exception verifying Sorgenia OTP")
                errors["base"] = "unknown"
            else:
                return await self._async_finish(tokens)

        return self.async_show_form(
            step_id="otp",
            data_schema=get_otp_schema(),
            errors=errors,
            description_placeholders={"phone": self._otp_phone},
        )

    async def _async_submit_credentials(
        self,
        user_input: dict[str, Any],
        step_id: str,
    ) -> config_entries.ConfigFlowResult:
        """Authenticate credentials or start the required OTP step."""
        try:
            tokens = await async_login(
                self.hass,
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
        except OtpRequired as err:
            return await self._async_start_otp(user_input, step_id, err)
        except SorgeniaApiAuthenticationError:
            return self._async_show_credentials_form(user_input, step_id, {"base": "invalid_auth"})
        except SorgeniaApiCommunicationError:
            return self._async_show_credentials_form(user_input, step_id, {"base": "cannot_connect"})
        except SorgeniaApiError:
            LOGGER.exception("Unexpected exception logging in to Sorgenia")
            return self._async_show_credentials_form(user_input, step_id, {"base": "unknown"})

        self._pending_credentials = user_input
        return await self._async_finish(tokens)

    async def _async_start_otp(
        self,
        user_input: dict[str, Any],
        step_id: str,
        otp_required: OtpRequired,
    ) -> config_entries.ConfigFlowResult:
        """Send an OTP and retain only the data needed for its verification."""
        if not otp_required.validated_phone:
            return self._async_show_credentials_form(user_input, step_id, {"base": "otp_phone_missing"})

        try:
            await async_send_otp(self.hass, user_input[CONF_USERNAME], otp_required.validated_phone)
        except SorgeniaApiAuthenticationError:
            return self._async_show_credentials_form(user_input, step_id, {"base": "otp_delivery_failed"})
        except SorgeniaApiCommunicationError:
            return self._async_show_credentials_form(user_input, step_id, {"base": "cannot_connect"})
        except SorgeniaApiError:
            LOGGER.exception("Unexpected exception sending Sorgenia OTP")
            return self._async_show_credentials_form(user_input, step_id, {"base": "unknown"})

        self._pending_credentials = user_input
        self._otp_phone = otp_required.validated_phone
        self._otp_token = otp_required.token
        return await self.async_step_otp()

    async def _async_finish(self, tokens: SorgeniaTokens) -> config_entries.ConfigFlowResult:
        """Create or update the entry with credentials and the latest tokens."""
        if self._pending_credentials is None:
            return self.async_abort(reason="unknown")

        data = {
            **{key: value for key, value in self._pending_credentials.items() if key != CONF_PASSWORD},
            CONF_ACCESS_TOKEN: tokens.access_token,
            CONF_REFRESH_TOKEN: tokens.refresh_token or "",
            CONF_VALIDATED_PHONE: tokens.validated_phone or self._otp_phone or "",
        }
        if self.source == SOURCE_REAUTH:
            data = {**self._get_reauth_entry().data, **data}
        elif self.source == SOURCE_RECONFIGURE:
            data = {**self._get_reconfigure_entry().data, **data}

        await self.async_set_unique_id(_client_code_unique_id(data[CONF_CLIENT_CODE]))

        if self.source == SOURCE_REAUTH:
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(self._get_reauth_entry(), data_updates=data)
        if self.source == SOURCE_RECONFIGURE:
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(self._get_reconfigure_entry(), data_updates=data)

        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Sorgenia", data=data)

    def _async_show_credentials_form(
        self,
        user_input: dict[str, Any],
        step_id: str,
        errors: dict[str, str],
    ) -> config_entries.ConfigFlowResult:
        """Re-show the credential form appropriate to the current flow source."""
        if step_id == "reauth":
            entry = self._get_reauth_entry()
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=get_reauth_schema(user_input[CONF_USERNAME]),
                errors=errors,
                description_placeholders={"name": entry.title},
            )
        if step_id == "reconfigure":
            return self.async_show_form(
                step_id="reconfigure",
                data_schema=get_reconfigure_schema(user_input[CONF_USERNAME]),
                errors=errors,
            )

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(user_input),
            errors=errors,
            description_placeholders={"documentation_url": integration.documentation or ""},
        )


def _client_code_unique_id(client_code: str) -> str:
    """Normalize the stable customer account identifier."""
    return client_code.strip().casefold()


__all__ = ["SorgeniaConfigFlowHandler"]
