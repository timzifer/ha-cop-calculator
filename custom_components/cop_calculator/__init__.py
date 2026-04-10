"""COP Calculator integration for Home Assistant.

Monitors heat pump efficiency by calculating COP (Coefficient of Performance)
from electrical energy consumption and thermal energy production sensors.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import COPDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up COP Calculator from a config entry."""
    coordinator = COPDataCoordinator(hass, entry)
    await coordinator.async_initialize()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a COP Calculator config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator: COPDataCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator.async_stop()

    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Handle options update."""
    coordinator: COPDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_update_options(entry)
