"""
Runtime data types for sorgenia.

Access pattern: entry.runtime_data.client / entry.runtime_data.coordinator
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from custom_components.sorgenia.sorgenia_api import SorgeniaApi
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import SorgeniaDataUpdateCoordinator


type SorgeniaConfigEntry = ConfigEntry[SorgeniaData]


@dataclass
class SorgeniaData:
    """Runtime data stored on the config entry after a successful setup."""

    client: SorgeniaApi
    coordinator: SorgeniaDataUpdateCoordinator
    integration: Integration
