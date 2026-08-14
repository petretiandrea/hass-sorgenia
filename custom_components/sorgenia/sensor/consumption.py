"""Consumption and cost sensors."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from custom_components.sorgenia.coordinator.base import SorgeniaConsumptionData, SorgeniaDataUpdateCoordinator
from custom_components.sorgenia.entity import SorgeniaEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util


@dataclass(frozen=True, kw_only=True)
class SorgeniaSensorEntityDescription(SensorEntityDescription):
    """Describe a Sorgenia sensor and how to read its coordinator data."""

    value_fn: Callable[[SorgeniaConsumptionData], StateType]
    last_reset_fn: Callable[[SorgeniaConsumptionData], datetime]


ENTITY_DESCRIPTIONS: tuple[SorgeniaSensorEntityDescription, ...] = (
    SorgeniaSensorEntityDescription(
        key="consumption",
        translation_key="consumption",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda data: data.get("consumption"),
        last_reset_fn=lambda data: dt_util.utc_from_timestamp(data["interval_start"]),
    ),
    SorgeniaSensorEntityDescription(
        key="cost",
        translation_key="cost",
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement=CURRENCY_EURO,
        value_fn=lambda data: data.get("cost"),
        last_reset_fn=lambda data: dt_util.utc_from_timestamp(data["interval_start"]),
    ),
)


class SorgeniaConsumptionSensor(SensorEntity, SorgeniaEntity):
    """Expose one consumption interval value from the coordinator."""

    entity_description: SorgeniaSensorEntityDescription

    def __init__(
        self,
        coordinator: SorgeniaDataUpdateCoordinator,
        entity_description: SorgeniaSensorEntityDescription,
    ) -> None:
        """Initialize a consumption or cost sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def last_reset(self) -> datetime:
        """Return the start of the current billing cycle."""
        return self.entity_description.last_reset_fn(self.coordinator.data)

    @property
    def native_value(self) -> StateType:
        """Return the value from the current billing interval."""
        return self.entity_description.value_fn(self.coordinator.data)
