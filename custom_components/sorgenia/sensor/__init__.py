"""Sorgenia sensor platform."""

from typing import TYPE_CHECKING

from .consumption import ENTITY_DESCRIPTIONS, SorgeniaConsumptionSensor

if TYPE_CHECKING:
    from custom_components.sorgenia.data import SorgeniaConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SorgeniaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sorgenia consumption sensors."""
    async_add_entities(
        SorgeniaConsumptionSensor(entry.runtime_data.coordinator, description) for description in ENTITY_DESCRIPTIONS
    )
