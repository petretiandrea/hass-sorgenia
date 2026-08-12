"""Number platform for sorgenia."""

from typing import TYPE_CHECKING

from .target_humidity import ENTITY_DESCRIPTIONS, SorgeniaHumidityNumber

# Acts on the device: the coordinator does not limit outbound calls.
PARALLEL_UPDATES = 1

if TYPE_CHECKING:
    from custom_components.sorgenia.data import SorgeniaConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SorgeniaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        SorgeniaHumidityNumber(entry.runtime_data.coordinator, description) for description in ENTITY_DESCRIPTIONS
    )
