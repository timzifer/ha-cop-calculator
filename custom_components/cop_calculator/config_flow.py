"""Config flow for COP Calculator integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ELECTRICAL_ENTITY,
    CONF_THERMAL_ENTITY,
    CONF_ELECTRICITY_PRICE,
    CONF_ELECTRICITY_PRICE_ENTITY,
    CONF_PRICE_TYPE,
    CONF_AVERAGING_PERIOD,
    CONF_MODE_ENTITY,
    CONF_MODE_HEATING_STATES,
    CONF_MODE_DHW_STATES,
    CONF_MODE_SIMULTANEOUS_STATES,
    CONF_DEFAULT_MODE,
    PRICE_TYPE_NONE,
    PRICE_TYPE_FIXED,
    PRICE_TYPE_SENSOR,
    DEFAULT_NAME,
    DEFAULT_AVERAGING_PERIOD,
    MODE_HEATING,
    MODE_DHW,
    MODE_SIMULTANEOUS,
)

_LOGGER = logging.getLogger(__name__)

PRICE_TYPE_OPTIONS = [
    selector.SelectOptionDict(value=PRICE_TYPE_NONE, label="No price"),
    selector.SelectOptionDict(value=PRICE_TYPE_FIXED, label="Fixed price"),
    selector.SelectOptionDict(value=PRICE_TYPE_SENSOR, label="Price sensor"),
]


DEFAULT_MODE_OPTIONS = [
    selector.SelectOptionDict(value=MODE_HEATING, label="Heating"),
    selector.SelectOptionDict(value=MODE_DHW, label="Hot Water (DHW)"),
    selector.SelectOptionDict(value=MODE_SIMULTANEOUS, label="Simultaneous"),
]


def _get_mode_entity_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build schema for the mode entity step."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Optional(
                CONF_MODE_ENTITY,
                description={"suggested_value": defaults.get(CONF_MODE_ENTITY)},
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(),
            ),
        }
    )


def _get_mode_matching_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build schema for the mode matching step."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Optional(
                CONF_MODE_HEATING_STATES,
                default=defaults.get(CONF_MODE_HEATING_STATES, ""),
            ): selector.TextSelector(),
            vol.Optional(
                CONF_MODE_DHW_STATES,
                default=defaults.get(CONF_MODE_DHW_STATES, ""),
            ): selector.TextSelector(),
            vol.Optional(
                CONF_MODE_SIMULTANEOUS_STATES,
                default=defaults.get(CONF_MODE_SIMULTANEOUS_STATES, ""),
            ): selector.TextSelector(),
        }
    )


def _get_default_mode_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build schema for the default mode step."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_DEFAULT_MODE,
                default=defaults.get(CONF_DEFAULT_MODE, MODE_HEATING),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=DEFAULT_MODE_OPTIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                ),
            ),
        }
    )


def _get_user_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build schema for the user step."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Optional(
                CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)
            ): selector.TextSelector(),
            vol.Required(
                CONF_ELECTRICAL_ENTITY,
                default=defaults.get(CONF_ELECTRICAL_ENTITY),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor"),
            ),
            vol.Required(
                CONF_THERMAL_ENTITY,
                default=defaults.get(CONF_THERMAL_ENTITY),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor"),
            ),
            vol.Optional(
                CONF_AVERAGING_PERIOD,
                default=defaults.get(CONF_AVERAGING_PERIOD, DEFAULT_AVERAGING_PERIOD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=120,
                    step=1,
                    unit_of_measurement="min",
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
        }
    )


def _get_pricing_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    """Build schema for the pricing step."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_PRICE_TYPE,
                default=defaults.get(CONF_PRICE_TYPE, PRICE_TYPE_NONE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=PRICE_TYPE_OPTIONS,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                ),
            ),
            vol.Optional(
                CONF_ELECTRICITY_PRICE,
                description={"suggested_value": defaults.get(CONF_ELECTRICITY_PRICE)},
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=2,
                    step=0.001,
                    unit_of_measurement="EUR/kWh",
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
            vol.Optional(
                CONF_ELECTRICITY_PRICE_ENTITY,
                description={"suggested_value": defaults.get(CONF_ELECTRICITY_PRICE_ENTITY)},
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor"),
            ),
        }
    )


class COPCalculatorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for COP Calculator."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._user_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the user configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate that entities are different
            if user_input[CONF_ELECTRICAL_ENTITY] == user_input[CONF_THERMAL_ENTITY]:
                errors["base"] = "same_entity"
            else:
                self._user_data = user_input
                return await self.async_step_mode()

        return self.async_show_form(
            step_id="user",
            data_schema=_get_user_schema(),
            errors=errors,
        )

    async def async_step_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the operating mode entity selection step."""
        if user_input is not None:
            mode_entity = user_input.get(CONF_MODE_ENTITY)
            self._user_data.update(user_input)
            if mode_entity:
                return await self.async_step_mode_matching()
            return await self.async_step_default_mode()

        return self.async_show_form(
            step_id="mode",
            data_schema=_get_mode_entity_schema(),
        )

    async def async_step_mode_matching(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the mode matching strings step (when entity is selected)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            heating_states = (
                user_input.get(CONF_MODE_HEATING_STATES, "") or ""
            ).strip()
            dhw_states = (
                user_input.get(CONF_MODE_DHW_STATES, "") or ""
            ).strip()
            if not heating_states:
                errors["base"] = "no_heating_states"
            elif not dhw_states:
                errors["base"] = "no_dhw_states"

            if not errors:
                self._user_data.update(user_input)
                return await self.async_step_pricing()

        return self.async_show_form(
            step_id="mode_matching",
            data_schema=_get_mode_matching_schema(),
            errors=errors,
        )

    async def async_step_default_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the default mode selection step (when no entity is selected)."""
        if user_input is not None:
            self._user_data.update(user_input)
            return await self.async_step_pricing()

        return self.async_show_form(
            step_id="default_mode",
            data_schema=_get_default_mode_schema(),
        )

    async def async_step_pricing(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the pricing configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            price_type = user_input.get(CONF_PRICE_TYPE, PRICE_TYPE_NONE)

            # Validate price configuration
            if price_type == PRICE_TYPE_FIXED and not user_input.get(
                CONF_ELECTRICITY_PRICE
            ):
                errors["base"] = "no_price"
            elif price_type == PRICE_TYPE_SENSOR and not user_input.get(
                CONF_ELECTRICITY_PRICE_ENTITY
            ):
                errors["base"] = "no_price_entity"
            else:
                # Merge user data and pricing data
                data = {**self._user_data, **user_input}

                # Clean up unused price fields
                if price_type == PRICE_TYPE_NONE:
                    data.pop(CONF_ELECTRICITY_PRICE, None)
                    data.pop(CONF_ELECTRICITY_PRICE_ENTITY, None)
                elif price_type == PRICE_TYPE_FIXED:
                    data.pop(CONF_ELECTRICITY_PRICE_ENTITY, None)
                elif price_type == PRICE_TYPE_SENSOR:
                    data.pop(CONF_ELECTRICITY_PRICE, None)

                # Clean up unused mode fields (mutually exclusive paths)
                if data.get(CONF_MODE_ENTITY):
                    # Mode entity path: remove default_mode
                    data.pop(CONF_DEFAULT_MODE, None)
                else:
                    # Default mode path: remove entity and matching strings
                    data.pop(CONF_MODE_ENTITY, None)
                    data.pop(CONF_MODE_HEATING_STATES, None)
                    data.pop(CONF_MODE_DHW_STATES, None)
                    data.pop(CONF_MODE_SIMULTANEOUS_STATES, None)

                name = data.get(CONF_NAME, DEFAULT_NAME)
                return self.async_create_entry(title=name, data=data)

        return self.async_show_form(
            step_id="pricing",
            data_schema=_get_pricing_schema(),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> COPCalculatorOptionsFlow:
        """Get the options flow for this handler."""
        return COPCalculatorOptionsFlow(config_entry)


class COPCalculatorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for COP Calculator."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        self._user_data: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial options step."""
        errors: dict[str, str] = {}
        defaults = {**self._config_entry.data}

        if user_input is not None:
            if user_input[CONF_ELECTRICAL_ENTITY] == user_input[CONF_THERMAL_ENTITY]:
                errors["base"] = "same_entity"
            else:
                self._user_data = user_input
                return await self.async_step_mode()

        return self.async_show_form(
            step_id="init",
            data_schema=_get_user_schema(defaults),
            errors=errors,
        )

    async def async_step_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the operating mode entity selection options step."""
        defaults = {**self._config_entry.data}

        if user_input is not None:
            mode_entity = user_input.get(CONF_MODE_ENTITY)
            self._user_data.update(user_input)
            if mode_entity:
                return await self.async_step_mode_matching()
            return await self.async_step_default_mode()

        return self.async_show_form(
            step_id="mode",
            data_schema=_get_mode_entity_schema(defaults),
        )

    async def async_step_mode_matching(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the mode matching strings options step."""
        errors: dict[str, str] = {}
        defaults = {**self._config_entry.data}

        if user_input is not None:
            heating_states = (
                user_input.get(CONF_MODE_HEATING_STATES, "") or ""
            ).strip()
            dhw_states = (
                user_input.get(CONF_MODE_DHW_STATES, "") or ""
            ).strip()
            if not heating_states:
                errors["base"] = "no_heating_states"
            elif not dhw_states:
                errors["base"] = "no_dhw_states"

            if not errors:
                self._user_data.update(user_input)
                return await self.async_step_pricing()

        return self.async_show_form(
            step_id="mode_matching",
            data_schema=_get_mode_matching_schema(defaults),
            errors=errors,
        )

    async def async_step_default_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the default mode selection options step."""
        defaults = {**self._config_entry.data}

        if user_input is not None:
            self._user_data.update(user_input)
            return await self.async_step_pricing()

        return self.async_show_form(
            step_id="default_mode",
            data_schema=_get_default_mode_schema(defaults),
        )

    async def async_step_pricing(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the pricing options step."""
        errors: dict[str, str] = {}
        defaults = {**self._config_entry.data}

        if user_input is not None:
            price_type = user_input.get(CONF_PRICE_TYPE, PRICE_TYPE_NONE)

            if price_type == PRICE_TYPE_FIXED and not user_input.get(
                CONF_ELECTRICITY_PRICE
            ):
                errors["base"] = "no_price"
            elif price_type == PRICE_TYPE_SENSOR and not user_input.get(
                CONF_ELECTRICITY_PRICE_ENTITY
            ):
                errors["base"] = "no_price_entity"
            else:
                data = {**self._user_data, **user_input}

                if price_type == PRICE_TYPE_NONE:
                    data.pop(CONF_ELECTRICITY_PRICE, None)
                    data.pop(CONF_ELECTRICITY_PRICE_ENTITY, None)
                elif price_type == PRICE_TYPE_FIXED:
                    data.pop(CONF_ELECTRICITY_PRICE_ENTITY, None)
                elif price_type == PRICE_TYPE_SENSOR:
                    data.pop(CONF_ELECTRICITY_PRICE, None)

                # Clean up unused mode fields (mutually exclusive paths)
                if data.get(CONF_MODE_ENTITY):
                    data.pop(CONF_DEFAULT_MODE, None)
                else:
                    data.pop(CONF_MODE_ENTITY, None)
                    data.pop(CONF_MODE_HEATING_STATES, None)
                    data.pop(CONF_MODE_DHW_STATES, None)
                    data.pop(CONF_MODE_SIMULTANEOUS_STATES, None)

                self.hass.config_entries.async_update_entry(
                    self._config_entry, data=data
                )
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="pricing",
            data_schema=_get_pricing_schema(defaults),
            errors=errors,
        )
