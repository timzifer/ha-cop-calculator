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

# Sensor types
SENSOR_TYPE_ENERGY = "energy"
SENSOR_TYPE_POWER = "power"

# Price types
PRICE_TYPE_NONE = "none"
PRICE_TYPE_FIXED = "fixed"
PRICE_TYPE_SENSOR = "sensor"

# Defaults
DEFAULT_NAME = "Heat Pump"
DEFAULT_AVERAGING_PERIOD = 15  # minutes

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

# Periods
PERIOD_DAILY = "daily"
PERIOD_WEEKLY = "weekly"
PERIOD_MONTHLY = "monthly"
PERIOD_YEARLY = "yearly"
PERIOD_TOTAL = "total"
