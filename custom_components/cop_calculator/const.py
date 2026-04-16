"""Constants for the COP Calculator integration."""

DOMAIN = "cop_calculator"
PLATFORMS = ["sensor"]

# Config keys
CONF_NAME = "name"
CONF_ELECTRICAL_ENTITY = "electrical_entity"
CONF_THERMAL_ENTITY = "thermal_entity"
CONF_ELECTRICAL_SENSOR_TYPE = "electrical_sensor_type"
CONF_THERMAL_SENSOR_TYPE = "thermal_sensor_type"
CONF_ELECTRICITY_PRICE = "electricity_price"
CONF_ELECTRICITY_PRICE_ENTITY = "electricity_price_entity"
CONF_PRICE_TYPE = "price_type"
CONF_AVERAGING_PERIOD = "averaging_period"

# Mode configuration keys
CONF_MODE_ENTITY = "mode_entity"
CONF_MODE_HEATING_STATES = "mode_heating_states"
CONF_MODE_DHW_STATES = "mode_dhw_states"
CONF_MODE_SIMULTANEOUS_STATES = "mode_simultaneous_states"
CONF_DEFAULT_MODE = "default_mode"

# Sensor types
SENSOR_TYPE_ENERGY = "energy"
SENSOR_TYPE_POWER = "power"
SENSOR_TYPE_ENERGY_WH = "energy_wh"
SENSOR_TYPE_POWER_W = "power_w"

# Price types
PRICE_TYPE_NONE = "none"
PRICE_TYPE_FIXED = "fixed"
PRICE_TYPE_SENSOR = "sensor"

# Defaults
DEFAULT_NAME = "Heat Pump"
DEFAULT_AVERAGING_PERIOD = 15  # minutes

# Mode identifiers
MODE_HEATING = "heating"
MODE_DHW = "dhw"
MODE_SIMULTANEOUS = "simultaneous"
MODE_UNKNOWN = "unknown"

# Sensor keys
SENSOR_COP_CURRENT = "cop_current"
SENSOR_COP_DAILY = "cop_daily"
SENSOR_COP_WEEKLY = "cop_weekly"
SENSOR_COP_MONTHLY = "cop_monthly"
SENSOR_COP_YEARLY = "cop_yearly"
SENSOR_COP_TOTAL = "cop_total"
SENSOR_ELECTRICAL_DAILY = "electrical_energy_daily"
SENSOR_ELECTRICAL_MONTHLY = "electrical_energy_monthly"
SENSOR_ELECTRICAL_YEARLY = "electrical_energy_yearly"
SENSOR_THERMAL_DAILY = "thermal_energy_daily"
SENSOR_THERMAL_MONTHLY = "thermal_energy_monthly"
SENSOR_THERMAL_YEARLY = "thermal_energy_yearly"
SENSOR_ENERGY_SAVINGS_DAILY = "energy_savings_daily"
SENSOR_COST_DAILY = "electricity_cost_daily"
SENSOR_COST_MONTHLY = "electricity_cost_monthly"
SENSOR_COST_YEARLY = "electricity_cost_yearly"
SENSOR_SAVINGS_COST_DAILY = "savings_cost_daily"

# Heating mode sensor keys
SENSOR_HEATING_COP_CURRENT = "heating_cop_current"
SENSOR_HEATING_COP_DAILY = "heating_cop_daily"
SENSOR_HEATING_COP_WEEKLY = "heating_cop_weekly"
SENSOR_HEATING_COP_MONTHLY = "heating_cop_monthly"
SENSOR_HEATING_COP_YEARLY = "heating_cop_yearly"
SENSOR_HEATING_COP_TOTAL = "heating_cop_total"
SENSOR_HEATING_ELECTRICAL_DAILY = "heating_electrical_energy_daily"
SENSOR_HEATING_ELECTRICAL_MONTHLY = "heating_electrical_energy_monthly"
SENSOR_HEATING_ELECTRICAL_YEARLY = "heating_electrical_energy_yearly"
SENSOR_HEATING_THERMAL_DAILY = "heating_thermal_energy_daily"
SENSOR_HEATING_THERMAL_MONTHLY = "heating_thermal_energy_monthly"
SENSOR_HEATING_THERMAL_YEARLY = "heating_thermal_energy_yearly"

# DHW mode sensor keys
SENSOR_DHW_COP_CURRENT = "dhw_cop_current"
SENSOR_DHW_COP_DAILY = "dhw_cop_daily"
SENSOR_DHW_COP_WEEKLY = "dhw_cop_weekly"
SENSOR_DHW_COP_MONTHLY = "dhw_cop_monthly"
SENSOR_DHW_COP_YEARLY = "dhw_cop_yearly"
SENSOR_DHW_COP_TOTAL = "dhw_cop_total"
SENSOR_DHW_ELECTRICAL_DAILY = "dhw_electrical_energy_daily"
SENSOR_DHW_ELECTRICAL_MONTHLY = "dhw_electrical_energy_monthly"
SENSOR_DHW_ELECTRICAL_YEARLY = "dhw_electrical_energy_yearly"
SENSOR_DHW_THERMAL_DAILY = "dhw_thermal_energy_daily"
SENSOR_DHW_THERMAL_MONTHLY = "dhw_thermal_energy_monthly"
SENSOR_DHW_THERMAL_YEARLY = "dhw_thermal_energy_yearly"

# Simultaneous mode sensor keys
SENSOR_SIMULTANEOUS_COP_CURRENT = "simultaneous_cop_current"
SENSOR_SIMULTANEOUS_COP_DAILY = "simultaneous_cop_daily"
SENSOR_SIMULTANEOUS_COP_WEEKLY = "simultaneous_cop_weekly"
SENSOR_SIMULTANEOUS_COP_MONTHLY = "simultaneous_cop_monthly"
SENSOR_SIMULTANEOUS_COP_YEARLY = "simultaneous_cop_yearly"
SENSOR_SIMULTANEOUS_COP_TOTAL = "simultaneous_cop_total"
SENSOR_SIMULTANEOUS_ELECTRICAL_DAILY = "simultaneous_electrical_energy_daily"
SENSOR_SIMULTANEOUS_ELECTRICAL_MONTHLY = "simultaneous_electrical_energy_monthly"
SENSOR_SIMULTANEOUS_ELECTRICAL_YEARLY = "simultaneous_electrical_energy_yearly"
SENSOR_SIMULTANEOUS_THERMAL_DAILY = "simultaneous_thermal_energy_daily"
SENSOR_SIMULTANEOUS_THERMAL_MONTHLY = "simultaneous_thermal_energy_monthly"
SENSOR_SIMULTANEOUS_THERMAL_YEARLY = "simultaneous_thermal_energy_yearly"

# Periods
PERIOD_DAILY = "daily"
PERIOD_WEEKLY = "weekly"
PERIOD_MONTHLY = "monthly"
PERIOD_YEARLY = "yearly"
PERIOD_TOTAL = "total"
