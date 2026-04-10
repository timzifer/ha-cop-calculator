# COP Calculator for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration that calculates the **Coefficient of Performance (COP)** of heat pumps by monitoring electrical energy consumption and thermal energy production.

## Features

- **COP Calculation** with configurable averaging period (default: 15 minutes) to account for delays between electrical input and thermal output
- **Multiple time periods**: Current, Daily, Weekly, Monthly, Yearly (SCOP), and Total COP
- **Energy tracking**: Daily, monthly, and yearly electrical and thermal energy consumption
- **Cost calculation**: Optional electricity cost tracking with fixed price or dynamic price sensor (e.g., Tibber, aWATTar)
- **Energy savings**: Shows how much energy is saved compared to direct electric heating
- **Flexible input**: Supports both energy counters (kWh) and power sensors (kW)
- **Persistent storage**: Values survive Home Assistant restarts
- **Multi-language**: English and German translations

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots menu (top right) and select "Custom repositories"
4. Add `https://github.com/timzifer/ha-cop-calculator` as an Integration
5. Search for "COP Calculator" and install it
6. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/cop_calculator` folder from this repository
2. Copy it to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **COP Calculator**
3. Follow the setup wizard:

### Step 1: Sensor Configuration

| Setting | Description |
|---------|-------------|
| **Name** | Display name for the heat pump device (default: "Heat Pump") |
| **Electrical energy sensor** | Your heat pump's electricity consumption sensor |
| **Electrical sensor type** | Energy counter (kWh, cumulative) or Power (kW, instantaneous) |
| **Thermal energy sensor** | Your heat pump's thermal energy/heat production sensor |
| **Thermal sensor type** | Energy counter (kWh, cumulative) or Power (kW, instantaneous) |
| **Averaging period** | Time window in minutes for current COP calculation (default: 15 min) |

### Step 2: Electricity Pricing (Optional)

| Setting | Description |
|---------|-------------|
| **Price mode** | No price / Fixed price / Price sensor |
| **Fixed electricity price** | Price in EUR/kWh (e.g., 0.30) |
| **Electricity price sensor** | Entity providing dynamic price (e.g., from Tibber or aWATTar) |

## Sensors

### COP Sensors

| Sensor | Description |
|--------|-------------|
| **COP Current** | COP averaged over the configured time window |
| **COP Daily** | COP for today (resets at midnight) |
| **COP Weekly** | COP for this week (resets Monday) |
| **COP Monthly** | COP for this month (resets 1st of month) |
| **SCOP (Yearly)** | Seasonal COP for this year (resets January 1st) |
| **COP Total** | COP since integration setup |

### Energy Sensors

| Sensor | Description |
|--------|-------------|
| **Electrical Energy Daily/Monthly/Yearly** | Electricity consumed by the heat pump |
| **Thermal Energy Daily/Monthly/Yearly** | Thermal energy produced by the heat pump |
| **Energy Savings Daily** | Thermal energy minus electrical energy (free energy from environment) |

### Cost Sensors (if pricing configured)

| Sensor | Description |
|--------|-------------|
| **Electricity Cost Daily/Monthly/Yearly** | Cost of electricity consumed |
| **Savings Cost Daily** | Cost savings compared to direct electric heating |

## Understanding COP and SCOP

**COP (Coefficient of Performance)** is the ratio of thermal energy output to electrical energy input:

```
COP = Thermal Energy (kWh) / Electrical Energy (kWh)
```

- A COP of **3.0** means the heat pump produces 3 kWh of heat for every 1 kWh of electricity consumed
- A COP of **1.0** would be equivalent to a simple electric heater
- Typical heat pump COP values range from **2.5 to 5.0** depending on conditions

**SCOP (Seasonal COP)** is the COP measured over an entire year, accounting for seasonal temperature variations. It's the most meaningful efficiency metric for comparing heat pumps.

## Why Averaging Instead of Instantaneous Values?

Heat pumps don't convert electrical energy to thermal energy instantaneously. There is a delay between the compressor consuming electricity and the resulting heat being measured. Using instantaneous values would produce wildly inaccurate COP readings.

This integration uses a **sliding window average** (configurable, default 15 minutes) to smooth out these delays and provide meaningful COP values.

## FAQ

**Q: What COP value should I expect?**
A: Typical air-source heat pumps achieve COP 2.5-4.0, ground-source heat pumps 3.5-5.0. Higher outdoor temperatures generally produce higher COP values.

**Q: Why is my COP showing as unavailable?**
A: COP becomes unavailable when the electrical energy delta is zero (heat pump is off) or when not enough data samples have been collected yet.

**Q: Can I use this with any heat pump?**
A: Yes, as long as you have sensors that measure the heat pump's electrical consumption and thermal energy production in Home Assistant.

**Q: What happens after a Home Assistant restart?**
A: All period start values and cumulative data are persisted to storage and restored after restart.

## License

MIT License - see [LICENSE](LICENSE) for details.
