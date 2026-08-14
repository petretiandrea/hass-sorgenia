"""Tests for the Sorgenia credential and OTP config flow."""

from unittest.mock import AsyncMock, patch

import pytest

from custom_components.sorgenia.const import (
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_CODE,
    CONF_OTP,
    CONF_POD,
    CONF_REFRESH_TOKEN,
    CONF_VALIDATED_PHONE,
    DOMAIN,
)
from custom_components.sorgenia.sorgenia_api import OtpRequired, OtpValidationError, SorgeniaTokens
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


@pytest.mark.unit
async def test_user_flow_creates_entry_with_tokens(hass: HomeAssistant) -> None:
    """A login without OTP stores the issued token pair in the entry."""
    tokens = SorgeniaTokens(
        access_token="access-token",
        refresh_token="refresh-token",
        username="test-user",
        validated_phone="+39000000000",
    )
    with patch(
        "custom_components.sorgenia.config_flow_handler.config_flow.async_login",
        new_callable=AsyncMock,
        return_value=tokens,
    ):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"next_step_id": "credentials"},
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "credentials"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "test-user", CONF_PASSWORD: "test-password", CONF_CLIENT_CODE: "client", CONF_POD: "pod"},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Sorgenia"
    assert result["data"] == {
        CONF_USERNAME: "test-user",
        CONF_CLIENT_CODE: "client",
        CONF_POD: "pod",
        CONF_ACCESS_TOKEN: "access-token",
        CONF_REFRESH_TOKEN: "refresh-token",
        CONF_VALIDATED_PHONE: "+39000000000",
    }


@pytest.mark.unit
async def test_user_flow_completes_otp_login(hass: HomeAssistant) -> None:
    """The flow sends and verifies an OTP before creating the entry."""
    otp_required = OtpRequired(
        "OTP required",
        token="otp-token",
        validated_phone="+39000000000",
        response={},
    )
    tokens = SorgeniaTokens(
        access_token="access-token",
        refresh_token="refresh-token",
        username="test-user",
    )
    with (
        patch(
            "custom_components.sorgenia.config_flow_handler.config_flow.async_login",
            new_callable=AsyncMock,
            side_effect=otp_required,
        ),
        patch(
            "custom_components.sorgenia.config_flow_handler.config_flow.async_send_otp",
            new_callable=AsyncMock,
        ) as send_otp,
        patch(
            "custom_components.sorgenia.config_flow_handler.config_flow.async_verify_otp",
            new_callable=AsyncMock,
            return_value=tokens,
        ) as verify_otp,
    ):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"next_step_id": "credentials"},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "test-user", CONF_PASSWORD: "test-password", CONF_CLIENT_CODE: "client", CONF_POD: "pod"},
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "otp"
        send_otp.assert_awaited_once_with(hass, "test-user", "+39000000000")

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_OTP: "123456"},
        )

    verify_otp.assert_awaited_once_with(hass, "test-user", "+39000000000", "123456", "otp-token")
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_ACCESS_TOKEN] == "access-token"
    assert result["data"][CONF_REFRESH_TOKEN] == "refresh-token"


@pytest.mark.unit
async def test_otp_flow_recovers_after_invalid_code(hass: HomeAssistant) -> None:
    """An invalid OTP leaves the verification form available for another attempt."""
    otp_required = OtpRequired(
        "OTP required",
        token="otp-token",
        validated_phone="+39000000000",
        response={},
    )
    tokens = SorgeniaTokens(access_token="access-token", refresh_token="refresh-token")
    with (
        patch(
            "custom_components.sorgenia.config_flow_handler.config_flow.async_login",
            new_callable=AsyncMock,
            side_effect=otp_required,
        ),
        patch(
            "custom_components.sorgenia.config_flow_handler.config_flow.async_send_otp",
            new_callable=AsyncMock,
        ),
        patch(
            "custom_components.sorgenia.config_flow_handler.config_flow.async_verify_otp",
            new_callable=AsyncMock,
            side_effect=[OtpValidationError("Invalid OTP"), tokens],
        ),
    ):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"next_step_id": "credentials"},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_USERNAME: "test-user", CONF_PASSWORD: "test-password", CONF_CLIENT_CODE: "client", CONF_POD: "pod"},
        )
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_OTP: "000000"})
        assert result["type"] is FlowResultType.FORM
        assert result["errors"] == {"base": "invalid_otp"}

        result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_OTP: "123456"})

    assert result["type"] is FlowResultType.CREATE_ENTRY


@pytest.mark.unit
async def test_tokens_flow_creates_entry_without_otp(hass: HomeAssistant) -> None:
    """Existing tokens are validated without calling the OTP login endpoints."""
    tokens = SorgeniaTokens(
        access_token="rotated-access-token",
        refresh_token="rotated-refresh-token",
        username="test-user",
    )
    with patch(
        "custom_components.sorgenia.config_flow_handler.config_flow.async_validate_tokens",
        new_callable=AsyncMock,
        return_value=tokens,
    ) as validate_tokens:
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {"next_step_id": "tokens"},
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "tokens"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test-user",
                CONF_CLIENT_CODE: "client",
                CONF_POD: "pod",
                CONF_ACCESS_TOKEN: "access-token",
                CONF_REFRESH_TOKEN: "refresh-token",
            },
        )

    validate_tokens.assert_awaited_once_with(
        hass,
        "test-user",
        "client",
        "pod",
        "access-token",
        "refresh-token",
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_ACCESS_TOKEN] == "rotated-access-token"
    assert result["data"][CONF_REFRESH_TOKEN] == "rotated-refresh-token"
