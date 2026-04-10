"""Data coordinator for COP Calculator integration."""

from __future__ import annotations

import logging
from collections import deque
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant, Event, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_ELECTRICAL_ENTITY,
    CONF_THERMAL_ENTITY,
    CONF_ELECTRICAL_SENSOR_TYPE,
    CONF_THERMAL_SENSOR_TYPE,
    CONF_ELECTRICITY_PRICE,
    CONF_ELECTRICITY_PRICE_ENTITY,
    CONF_PRICE_TYPE,
    CONF_AVERAGING_PERIOD,
    SENSOR_TYPE_POWER,
    PRICE_TYPE_FIXED,
    PRICE_TYPE_SENSOR,
    PERIOD_DAILY,
    PERIOD_WEEKLY,
    PERIOD_MONTHLY,
    PERIOD_YEARLY,
    PERIOD_TOTAL,
    DEFAULT_AVERAGING_PERIOD,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY_PREFIX = f"{DOMAIN}.coordinator"


class COPDataCoordinator:
    """Coordinator that tracks energy data and calculates COP values."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry
        self._listeners: list[callable] = []
        self._unsub_state_listeners: list[callable] = []
        self._unsub_time_listeners: list[callable] = []
        self._update_callbacks: list[callable] = []

        # Configuration
        self._electrical_entity: str = entry.data[CONF_ELECTRICAL_ENTITY]
        self._thermal_entity: str = entry.data[CONF_THERMAL_ENTITY]
        self._electrical_type: str = entry.data[CONF_ELECTRICAL_SENSOR_TYPE]
        self._thermal_type: str = entry.data[CONF_THERMAL_SENSOR_TYPE]
        self._averaging_period: int = entry.data.get(
            CONF_AVERAGING_PERIOD, DEFAULT_AVERAGING_PERIOD
        )
        self._price_type: str = entry.data.get(CONF_PRICE_TYPE, "none")
        self._fixed_price: float | None = entry.data.get(CONF_ELECTRICITY_PRICE)
        self._price_entity: str | None = entry.data.get(CONF_ELECTRICITY_PRICE_ENTITY)

        # Sliding window samples: (timestamp, electrical_cumulative, thermal_cumulative)
        self._samples: deque[tuple[datetime, float, float]] = deque()

        # For power→energy integration (trapezoid rule)
        self._last_electrical_power: float | None = None
        self._last_electrical_power_time: datetime | None = None
        self._last_thermal_power: float | None = None
        self._last_thermal_power_time: datetime | None = None

        # Cumulative energy values (used when input is power sensors)
        self._cumulative_electrical: float | None = None
        self._cumulative_thermal: float | None = None

        # Period start values: {period: (electrical_start, thermal_start)}
        self._period_starts: dict[str, tuple[float, float]] = {}

        # Total start values (never reset)
        self._total_electrical_start: float | None = None
        self._total_thermal_start: float | None = None

        # Track whether we have received real data from sensors
        self._has_real_data: bool = False

        # Current computed values
        self.data: dict[str, float | None] = {}

        # Persistent storage
        self._store = Store(
            hass, STORAGE_VERSION, f"{STORAGE_KEY_PREFIX}.{entry.entry_id}"
        )

    async def async_initialize(self) -> None:
        """Initialize the coordinator: restore state and set up listeners."""
        await self._async_restore_state()
        self._read_initial_state()
        self._setup_state_listeners()
        self._setup_time_listeners()
        if self._has_real_data:
            self._update_data()

    def _read_initial_state(self) -> None:
        """Read current state of input sensors from HA to avoid starting at 0."""
        for entity_id, sensor_type, is_electrical in [
            (self._electrical_entity, self._electrical_type, True),
            (self._thermal_entity, self._thermal_type, False),
        ]:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in ("unknown", "unavailable"):
                continue
            try:
                value = float(state.state)
            except (ValueError, TypeError):
                continue

            if is_electrical:
                if sensor_type == SENSOR_TYPE_POWER:
                    self._last_electrical_power = value
                    self._last_electrical_power_time = dt_util.utcnow()
                    if self._cumulative_electrical is None:
                        self._cumulative_electrical = 0.0
                else:
                    self._cumulative_electrical = value
            else:
                if sensor_type == SENSOR_TYPE_POWER:
                    self._last_thermal_power = value
                    self._last_thermal_power_time = dt_util.utcnow()
                    if self._cumulative_thermal is None:
                        self._cumulative_thermal = 0.0
                else:
                    self._cumulative_thermal = value

        self._has_real_data = (
            self._cumulative_electrical is not None
            and self._cumulative_thermal is not None
        )

    def _setup_state_listeners(self) -> None:
        """Set up state change listeners for input entities."""
        entities = [self._electrical_entity, self._thermal_entity]
        self._unsub_state_listeners.append(
            async_track_state_change_event(
                self.hass, entities, self._async_state_changed
            )
        )

    def _setup_time_listeners(self) -> None:
        """Set up time-based listeners for period resets."""
        # Daily reset at midnight
        self._unsub_time_listeners.append(
            async_track_time_change(
                self.hass, self._async_daily_reset, hour=0, minute=0, second=0
            )
        )

    @callback
    def async_add_update_callback(self, cb: callable) -> None:
        """Register a callback for data updates."""
        self._update_callbacks.append(cb)

    @callback
    def async_remove_update_callback(self, cb: callable) -> None:
        """Remove a callback."""
        if cb in self._update_callbacks:
            self._update_callbacks.remove(cb)

    def _notify_update(self) -> None:
        """Notify all registered callbacks about data update."""
        for cb in self._update_callbacks:
            cb()

    @callback
    def _async_state_changed(self, event: Event) -> None:
        """Handle state change events from input sensors."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return

        try:
            value = float(new_state.state)
        except (ValueError, TypeError):
            return

        now = dt_util.utcnow()

        if entity_id == self._electrical_entity:
            self._process_electrical_value(value, now)
        elif entity_id == self._thermal_entity:
            self._process_thermal_value(value, now)

        # Only process data once we have values from both sensors
        if self._cumulative_electrical is None or self._cumulative_thermal is None:
            return

        # Initialize period starts on first real data
        if not self._has_real_data:
            self._has_real_data = True
            self._initialize_period_starts()

        self._update_samples(now)
        self._update_data()
        self._notify_update()

        # Persist state periodically
        self.hass.async_create_task(self._async_save_state())

    def _process_electrical_value(self, value: float, now: datetime) -> None:
        """Process a new electrical sensor value."""
        if self._electrical_type == SENSOR_TYPE_POWER:
            # Power (kW) → integrate to energy (kWh)
            if self._cumulative_electrical is None:
                self._cumulative_electrical = 0.0
            if (
                self._last_electrical_power is not None
                and self._last_electrical_power_time is not None
            ):
                dt_hours = (
                    now - self._last_electrical_power_time
                ).total_seconds() / 3600.0
                if dt_hours > 0 and dt_hours < 1:  # Skip unreasonable gaps
                    # Trapezoid rule
                    energy = (
                        (self._last_electrical_power + value) / 2.0 * dt_hours
                    )
                    self._cumulative_electrical += energy
            self._last_electrical_power = value
            self._last_electrical_power_time = now
        else:
            # Energy (kWh) — use directly
            self._cumulative_electrical = value

    def _process_thermal_value(self, value: float, now: datetime) -> None:
        """Process a new thermal sensor value."""
        if self._thermal_type == SENSOR_TYPE_POWER:
            # Power (kW) → integrate to energy (kWh)
            if self._cumulative_thermal is None:
                self._cumulative_thermal = 0.0
            if (
                self._last_thermal_power is not None
                and self._last_thermal_power_time is not None
            ):
                dt_hours = (
                    now - self._last_thermal_power_time
                ).total_seconds() / 3600.0
                if dt_hours > 0 and dt_hours < 1:  # Skip unreasonable gaps
                    energy = (self._last_thermal_power + value) / 2.0 * dt_hours
                    self._cumulative_thermal += energy
            self._last_thermal_power = value
            self._last_thermal_power_time = now
        else:
            # Energy (kWh) — use directly
            self._cumulative_thermal = value

    def _initialize_period_starts(self) -> None:
        """Initialize period starts from current values when first real data arrives."""
        electrical = self._cumulative_electrical
        thermal = self._cumulative_thermal
        if electrical is None or thermal is None:
            return

        if self._total_electrical_start is None:
            self._total_electrical_start = electrical
        if self._total_thermal_start is None:
            self._total_thermal_start = thermal

        for period in (PERIOD_DAILY, PERIOD_WEEKLY, PERIOD_MONTHLY, PERIOD_YEARLY):
            if period not in self._period_starts:
                self._period_starts[period] = (electrical, thermal)

    def _update_samples(self, now: datetime) -> None:
        """Update the sliding window of samples."""
        self._samples.append(
            (now, self._cumulative_electrical, self._cumulative_thermal)
        )

        # Remove samples outside the averaging window
        cutoff = now - timedelta(minutes=self._averaging_period)
        while self._samples and self._samples[0][0] < cutoff:
            self._samples.popleft()

    def _get_current_electrical(self) -> float | None:
        """Get current cumulative electrical energy."""
        return self._cumulative_electrical

    def _get_current_thermal(self) -> float | None:
        """Get current cumulative thermal energy."""
        return self._cumulative_thermal

    def _get_electricity_price(self) -> float | None:
        """Get the current electricity price."""
        if self._price_type == PRICE_TYPE_FIXED:
            return self._fixed_price
        if self._price_type == PRICE_TYPE_SENSOR and self._price_entity:
            state = self.hass.states.get(self._price_entity)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    return float(state.state)
                except (ValueError, TypeError):
                    return None
        return None

    def _calculate_cop(
        self, thermal_delta: float, electrical_delta: float
    ) -> float | None:
        """Calculate COP from energy deltas."""
        if electrical_delta <= 0:
            return None
        cop = thermal_delta / electrical_delta
        # Sanity check: COP should be between 0 and ~15
        if cop < 0 or cop > 20:
            return None
        return round(cop, 2)

    def _update_data(self) -> None:
        """Recalculate all sensor values."""
        electrical = self._get_current_electrical()
        thermal = self._get_current_thermal()

        # Don't calculate anything without real sensor data
        if electrical is None or thermal is None:
            return

        # Initialize starts from real data (not from 0.0 defaults)
        if self._total_electrical_start is None:
            self._total_electrical_start = electrical
        if self._total_thermal_start is None:
            self._total_thermal_start = thermal

        for period in (PERIOD_DAILY, PERIOD_WEEKLY, PERIOD_MONTHLY, PERIOD_YEARLY):
            if period not in self._period_starts:
                self._period_starts[period] = (electrical, thermal)

        # Current COP (sliding window average)
        cop_current = None
        if len(self._samples) >= 2:
            oldest = self._samples[0]
            newest = self._samples[-1]
            elec_delta = newest[1] - oldest[1]
            therm_delta = newest[2] - oldest[2]
            cop_current = self._calculate_cop(therm_delta, elec_delta)

        # Period COPs
        period_data: dict[str, tuple[float, float]] = {}
        for period in (PERIOD_DAILY, PERIOD_WEEKLY, PERIOD_MONTHLY, PERIOD_YEARLY):
            start = self._period_starts.get(period, (electrical, thermal))
            elec_delta = electrical - start[0]
            therm_delta = thermal - start[1]
            period_data[period] = (elec_delta, therm_delta)

        # Total
        total_elec = electrical - (self._total_electrical_start or electrical)
        total_therm = thermal - (self._total_thermal_start or thermal)

        price = self._get_electricity_price()

        self.data = {
            # COP values
            "cop_current": cop_current,
            "cop_daily": self._calculate_cop(
                period_data[PERIOD_DAILY][1], period_data[PERIOD_DAILY][0]
            ),
            "cop_weekly": self._calculate_cop(
                period_data[PERIOD_WEEKLY][1], period_data[PERIOD_WEEKLY][0]
            ),
            "cop_monthly": self._calculate_cop(
                period_data[PERIOD_MONTHLY][1], period_data[PERIOD_MONTHLY][0]
            ),
            "cop_yearly": self._calculate_cop(
                period_data[PERIOD_YEARLY][1], period_data[PERIOD_YEARLY][0]
            ),
            "cop_total": self._calculate_cop(total_therm, total_elec),
            # Daily energy
            "electrical_energy_daily": round(period_data[PERIOD_DAILY][0], 3),
            "thermal_energy_daily": round(period_data[PERIOD_DAILY][1], 3),
            # Monthly energy
            "electrical_energy_monthly": round(period_data[PERIOD_MONTHLY][0], 3),
            "thermal_energy_monthly": round(period_data[PERIOD_MONTHLY][1], 3),
            # Yearly energy
            "electrical_energy_yearly": round(period_data[PERIOD_YEARLY][0], 3),
            "thermal_energy_yearly": round(period_data[PERIOD_YEARLY][1], 3),
            # Energy savings (thermal - electrical = free energy from environment)
            "energy_savings_daily": round(
                max(0, period_data[PERIOD_DAILY][1] - period_data[PERIOD_DAILY][0]), 3
            ),
        }

        # Cost calculations (only if price is available)
        if price is not None:
            self.data["electricity_cost_daily"] = round(
                period_data[PERIOD_DAILY][0] * price, 2
            )
            self.data["electricity_cost_monthly"] = round(
                period_data[PERIOD_MONTHLY][0] * price, 2
            )
            self.data["electricity_cost_yearly"] = round(
                period_data[PERIOD_YEARLY][0] * price, 2
            )
            savings_kwh = max(
                0, period_data[PERIOD_DAILY][1] - period_data[PERIOD_DAILY][0]
            )
            self.data["savings_cost_daily"] = round(savings_kwh * price, 2)
        else:
            self.data["electricity_cost_daily"] = None
            self.data["electricity_cost_monthly"] = None
            self.data["electricity_cost_yearly"] = None
            self.data["savings_cost_daily"] = None

    @callback
    def _async_daily_reset(self, now: datetime) -> None:
        """Handle daily reset at midnight."""
        electrical = self._get_current_electrical()
        thermal = self._get_current_thermal()
        local_now = dt_util.now()

        # Always reset daily
        self._period_starts[PERIOD_DAILY] = (electrical, thermal)

        # Reset weekly on Monday
        if local_now.weekday() == 0:
            self._period_starts[PERIOD_WEEKLY] = (electrical, thermal)

        # Reset monthly on the 1st
        if local_now.day == 1:
            self._period_starts[PERIOD_MONTHLY] = (electrical, thermal)

            # Reset yearly on January 1st
            if local_now.month == 1:
                self._period_starts[PERIOD_YEARLY] = (electrical, thermal)

        self._update_data()
        self._notify_update()
        self.hass.async_create_task(self._async_save_state())

    async def _async_save_state(self) -> None:
        """Persist state to storage."""
        data = {
            "cumulative_electrical": self._cumulative_electrical,
            "cumulative_thermal": self._cumulative_thermal,
            "total_electrical_start": self._total_electrical_start,
            "total_thermal_start": self._total_thermal_start,
            "period_starts": {
                k: list(v) for k, v in self._period_starts.items()
            },
            "last_electrical_power": self._last_electrical_power,
            "last_thermal_power": self._last_thermal_power,
        }
        await self._store.async_save(data)

    async def _async_restore_state(self) -> None:
        """Restore state from storage."""
        data = await self._store.async_load()
        if data is None:
            return

        stored_electrical = data.get("cumulative_electrical")
        stored_thermal = data.get("cumulative_thermal")
        if stored_electrical is not None:
            self._cumulative_electrical = stored_electrical
        if stored_thermal is not None:
            self._cumulative_thermal = stored_thermal

        self._total_electrical_start = data.get("total_electrical_start")
        self._total_thermal_start = data.get("total_thermal_start")
        self._last_electrical_power = data.get("last_electrical_power")
        self._last_thermal_power = data.get("last_thermal_power")

        period_starts = data.get("period_starts", {})
        for k, v in period_starts.items():
            if isinstance(v, list) and len(v) == 2:
                self._period_starts[k] = (v[0], v[1])

        # Mark as having real data if we successfully restored values
        if self._cumulative_electrical is not None and self._cumulative_thermal is not None:
            self._has_real_data = True

    @callback
    def async_stop(self) -> None:
        """Stop the coordinator and remove listeners."""
        for unsub in self._unsub_state_listeners:
            unsub()
        self._unsub_state_listeners.clear()

        for unsub in self._unsub_time_listeners:
            unsub()
        self._unsub_time_listeners.clear()

    async def async_update_options(self, entry: ConfigEntry) -> None:
        """Handle options update."""
        self.entry = entry
        self._electrical_entity = entry.data[CONF_ELECTRICAL_ENTITY]
        self._thermal_entity = entry.data[CONF_THERMAL_ENTITY]
        self._electrical_type = entry.data[CONF_ELECTRICAL_SENSOR_TYPE]
        self._thermal_type = entry.data[CONF_THERMAL_SENSOR_TYPE]
        self._averaging_period = entry.data.get(
            CONF_AVERAGING_PERIOD, DEFAULT_AVERAGING_PERIOD
        )
        self._price_type = entry.data.get(CONF_PRICE_TYPE, "none")
        self._fixed_price = entry.data.get(CONF_ELECTRICITY_PRICE)
        self._price_entity = entry.data.get(CONF_ELECTRICITY_PRICE_ENTITY)

        # Re-setup state listeners
        for unsub in self._unsub_state_listeners:
            unsub()
        self._unsub_state_listeners.clear()
        self._setup_state_listeners()

        self._update_data()
        self._notify_update()
