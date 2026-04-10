"""Sensor platform for COP Calculator integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_PRICE_TYPE,
    PRICE_TYPE_NONE,
    DEFAULT_NAME,
    SENSOR_COP_CURRENT,
    SENSOR_COP_DAILY,
    SENSOR_COP_WEEKLY,
    SENSOR_COP_MONTHLY,
    SENSOR_COP_YEARLY,
    SENSOR_COP_TOTAL,
    SENSOR_ELECTRICAL_DAILY,
    SENSOR_ELECTRICAL_MONTHLY,
    SENSOR_ELECTRICAL_YEARLY,
    SENSOR_THERMAL_DAILY,
    SENSOR_THERMAL_MONTHLY,
    SENSOR_THERMAL_YEARLY,
    SENSOR_ENERGY_SAVINGS_DAILY,
    SENSOR_COST_DAILY,
    SENSOR_COST_MONTHLY,
    SENSOR_COST_YEARLY,
    SENSOR_SAVINGS_COST_DAILY,
)
from .coordinator import COPDataCoordinator

_LOGGER = logging.getLogger(__name__)


SENSOR_DESCRIPTIONS: dict[str, dict[str, Any]] = {
    SENSOR_COP_CURRENT: {
        "name_en": "COP Current",
        "name_de": "COP Aktuell",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": None,
        "precision": 2,
        "requires_price": False,
    },
    SENSOR_COP_DAILY: {
        "name_en": "COP Daily",
        "name_de": "COP Täglich",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": None,
        "precision": 2,
        "requires_price": False,
    },
    SENSOR_COP_WEEKLY: {
        "name_en": "COP Weekly",
        "name_de": "COP Wöchentlich",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": None,
        "precision": 2,
        "requires_price": False,
    },
    SENSOR_COP_MONTHLY: {
        "name_en": "COP Monthly",
        "name_de": "COP Monatlich",
        "icon": "mdi:gauge",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": None,
        "precision": 2,
        "requires_price": False,
    },
    SENSOR_COP_YEARLY: {
        "name_en": "SCOP (Yearly)",
        "name_de": "SCOP (Jährlich)",
        "icon": "mdi:chart-line",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": None,
        "precision": 2,
        "requires_price": False,
    },
    SENSOR_COP_TOTAL: {
        "name_en": "COP Total",
        "name_de": "COP Gesamt",
        "icon": "mdi:chart-line",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": None,
        "precision": 2,
        "requires_price": False,
    },
    SENSOR_ELECTRICAL_DAILY: {
        "name_en": "Electrical Energy Daily",
        "name_de": "Elektrische Energie Täglich",
        "icon": "mdi:flash",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "kWh",
        "precision": 1,
        "requires_price": False,
    },
    SENSOR_ELECTRICAL_MONTHLY: {
        "name_en": "Electrical Energy Monthly",
        "name_de": "Elektrische Energie Monatlich",
        "icon": "mdi:flash",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "kWh",
        "precision": 1,
        "requires_price": False,
    },
    SENSOR_ELECTRICAL_YEARLY: {
        "name_en": "Electrical Energy Yearly",
        "name_de": "Elektrische Energie Jährlich",
        "icon": "mdi:flash",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "kWh",
        "precision": 1,
        "requires_price": False,
    },
    SENSOR_THERMAL_DAILY: {
        "name_en": "Thermal Energy Daily",
        "name_de": "Thermische Energie Täglich",
        "icon": "mdi:fire",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "kWh",
        "precision": 1,
        "requires_price": False,
    },
    SENSOR_THERMAL_MONTHLY: {
        "name_en": "Thermal Energy Monthly",
        "name_de": "Thermische Energie Monatlich",
        "icon": "mdi:fire",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "kWh",
        "precision": 1,
        "requires_price": False,
    },
    SENSOR_THERMAL_YEARLY: {
        "name_en": "Thermal Energy Yearly",
        "name_de": "Thermische Energie Jährlich",
        "icon": "mdi:fire",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "kWh",
        "precision": 1,
        "requires_price": False,
    },
    SENSOR_ENERGY_SAVINGS_DAILY: {
        "name_en": "Energy Savings Daily",
        "name_de": "Energieeinsparung Täglich",
        "icon": "mdi:leaf",
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "kWh",
        "precision": 1,
        "requires_price": False,
    },
    SENSOR_COST_DAILY: {
        "name_en": "Electricity Cost Daily",
        "name_de": "Stromkosten Täglich",
        "icon": "mdi:currency-eur",
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "EUR",
        "precision": 2,
        "requires_price": True,
    },
    SENSOR_COST_MONTHLY: {
        "name_en": "Electricity Cost Monthly",
        "name_de": "Stromkosten Monatlich",
        "icon": "mdi:currency-eur",
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "EUR",
        "precision": 2,
        "requires_price": True,
    },
    SENSOR_COST_YEARLY: {
        "name_en": "Electricity Cost Yearly",
        "name_de": "Stromkosten Jährlich",
        "icon": "mdi:currency-eur",
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "EUR",
        "precision": 2,
        "requires_price": True,
    },
    SENSOR_SAVINGS_COST_DAILY: {
        "name_en": "Savings Cost Daily",
        "name_de": "Eingesparte Kosten Täglich",
        "icon": "mdi:piggy-bank",
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL,
        "unit": "EUR",
        "precision": 2,
        "requires_price": True,
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up COP Calculator sensors from a config entry."""
    coordinator: COPDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    price_type = entry.data.get(CONF_PRICE_TYPE, PRICE_TYPE_NONE)

    entities: list[COPSensor] = []

    for sensor_key, description in SENSOR_DESCRIPTIONS.items():
        # Skip cost sensors if no price configured
        if description["requires_price"] and price_type == PRICE_TYPE_NONE:
            continue

        entities.append(
            COPSensor(
                coordinator=coordinator,
                entry=entry,
                sensor_key=sensor_key,
                device_name=name,
                description=description,
            )
        )

    async_add_entities(entities)


class COPSensor(RestoreEntity, SensorEntity):
    """Sensor entity for COP Calculator."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: COPDataCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        device_name: str,
        description: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._entry = entry
        self._sensor_key = sensor_key
        self._device_name = device_name

        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_translation_key = sensor_key
        self._attr_icon = description["icon"]
        self._attr_device_class = description["device_class"]
        self._attr_state_class = description["state_class"]
        self._attr_native_unit_of_measurement = description["unit"]
        self._attr_suggested_display_precision = description["precision"]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._device_name,
            manufacturer="COP Calculator",
            model="Energy Monitor",
            sw_version="1.0.0",
        )

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self._coordinator.data.get(self._sensor_key)

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        await super().async_added_to_hass()

        # Restore previous state
        last_state = await self.async_get_last_state()
        if last_state and last_state.state not in ("unknown", "unavailable"):
            try:
                restored = float(last_state.state)
                if self._sensor_key not in self._coordinator.data:
                    self._coordinator.data[self._sensor_key] = restored
            except (ValueError, TypeError):
                pass

        self._coordinator.async_add_update_callback(self._handle_update)

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        self._coordinator.async_remove_update_callback(self._handle_update)

    @callback
    def _handle_update(self) -> None:
        """Handle data update from coordinator."""
        self.async_write_ha_state()
