"""
Custom integration to integrate sorgenia with Home Assistant.

For more details about this integration, please refer to:
https://github.com/petretiandrea/hass-sorgenia
"""

from datetime import timedelta
from typing import TYPE_CHECKING

from custom_components.sorgenia.sorgenia_api import SorgeniaApi, SorgeniaAuth, SorgeniaTokens
from homeassistant.const import CONF_USERNAME, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

from .const import (
    BIDGELY_USER_ID,
    CONF_ACCESS_TOKEN,
    CONF_CLIENT_CODE,
    CONF_POD,
    CONF_REFRESH_TOKEN,
    CONF_UPDATE_INTERVAL_HOURS,
    CONF_VALIDATED_PHONE,
    DEFAULT_UPDATE_INTERVAL_HOURS,
    DOMAIN,
    LOGGER,
    SORGENIA_BASIC_AUTH,
    SORGENIA_SUBSCRIPTION_KEY,
)
from .coordinator import SorgeniaDataUpdateCoordinator
from .data import SorgeniaData
from .service_actions import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SorgeniaConfigEntry

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """
    Register the service actions.

    Returns:
        True once the actions are registered.

    """
    await async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SorgeniaConfigEntry,
) -> bool:
    """
    Set up a config entry.

    Returns:
        True once the coordinator has data and every platform is forwarded.

    """

    async def async_store_tokens(tokens: SorgeniaTokens) -> None:
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_ACCESS_TOKEN: tokens.access_token,
                CONF_REFRESH_TOKEN: tokens.refresh_token or "",
                CONF_VALIDATED_PHONE: tokens.validated_phone or "",
            },
        )

    auth = SorgeniaAuth(
        async_get_clientsession(hass),
        subscription_key=SORGENIA_SUBSCRIPTION_KEY,
        basic_auth=SORGENIA_BASIC_AUTH,
        tokens=SorgeniaTokens(
            access_token=entry.data[CONF_ACCESS_TOKEN],
            refresh_token=entry.data.get(CONF_REFRESH_TOKEN) or None,
            username=entry.data[CONF_USERNAME],
            validated_phone=entry.data.get(CONF_VALIDATED_PHONE) or None,
        ),
        token_updated=async_store_tokens,
    )
    client = SorgeniaApi(
        auth,
        client_code=entry.data[CONF_CLIENT_CODE],
        pod=entry.data[CONF_POD],
        bidgely_user_id=BIDGELY_USER_ID,
        subscription_key=SORGENIA_SUBSCRIPTION_KEY,
    )

    interval_hours = float(entry.options.get(CONF_UPDATE_INTERVAL_HOURS, DEFAULT_UPDATE_INTERVAL_HOURS))
    coordinator = SorgeniaDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        update_interval=timedelta(hours=interval_hours),
        always_update=False,
    )

    entry.runtime_data = SorgeniaData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: SorgeniaConfigEntry,
) -> bool:
    """
    Unload a config entry.

    Returns:
        True if every platform unloaded cleanly.

    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
