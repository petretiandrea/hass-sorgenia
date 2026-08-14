"""Data update coordinator for sorgenia."""

from typing import TYPE_CHECKING, TypedDict

from custom_components.sorgenia.const import DOMAIN
from custom_components.sorgenia.sorgenia_api import SorgeniaApiAuthenticationError, SorgeniaApiError
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from custom_components.sorgenia.data import SorgeniaConfigEntry


class SorgeniaConsumptionData(TypedDict):
    """Consumption data exposed to the integration entities."""

    consumption: float
    cost: float


class SorgeniaDataUpdateCoordinator(DataUpdateCoordinator[SorgeniaConsumptionData]):
    """Fetch the device state once per interval and hand it to every entity."""

    config_entry: SorgeniaConfigEntry

    async def _async_update_data(self) -> SorgeniaConsumptionData:
        """
        Fetch the current device state.

        Returns:
            The payload entities read by key.

        Raises:
            ConfigEntryAuthFailed: If the credentials were rejected; triggers reauth.
            UpdateFailed: If the fetch failed for any other reason.

        """
        try:
            details = await self.config_entry.runtime_data.client.async_get_usage_chart_details()
        except SorgeniaApiAuthenticationError as exception:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="authentication_failed",
            ) from exception
        except SorgeniaApiError as exception:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
            ) from exception
        else:
            interval = details.ongoing_interval
            if interval is None:
                raise UpdateFailed("Bidgely did not return the ongoing billing interval")
            return {"consumption": interval.consumption, "cost": interval.cost}
