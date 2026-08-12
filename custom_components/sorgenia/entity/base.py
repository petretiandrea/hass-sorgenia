"""Base entity class for sorgenia."""

from typing import TYPE_CHECKING

from custom_components.sorgenia.const import ATTRIBUTION
from custom_components.sorgenia.coordinator import SorgeniaDataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class SorgeniaEntity(CoordinatorEntity[SorgeniaDataUpdateCoordinator]):
    """
    Base entity providing device info, unique ID and attribution.

    The unique ID is `{entry_id}_{key}`, the documented identifier of last resort.
    A real integration switches to the device's serial, MAC or account ID before its
    first release, because changing it afterwards needs a registry migration.
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SorgeniaDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name=coordinator.config_entry.title,
            manufacturer="Sorgenia",
            model=coordinator.data["model"],
            serial_number=coordinator.data["serial_number"],
            sw_version=coordinator.data["sw_version"],
        )
