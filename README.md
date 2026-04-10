# EGD Power Data — Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/blesk89/HomeAssistant-EGD-distribuce24.svg)](https://github.com/blesk89/HomeAssistant-EGD-distribuce24/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Home Assistant integration for downloading smart meter data from [EG.D distribuce24](https://portal.distribuce24.cz) portal via OpenAPI.

Supports **electricity consumption** and **solar production** data in 15-minute intervals, fully compatible with the HA Energy dashboard.

---

## Features

- ⚡ Electricity consumption (kWh) — profile ICC1
- ☀️ Solar production / grid feed-in (kWh) — profile ISC1
- 📊 Full support for HA Energy dashboard
- 🔄 Automatic daily refresh (data published by EG.D from 10:00 the next day)
- 📝 Rotating log file (max 1 MB, 3 backups)
- 🔒 Secure token handling (no plaintext logging)

---

## Requirements

- Smart electricity meter type **A or B** (does NOT support type C — standard household meters without remote reading)
- Access to [portal.distribuce24.cz](https://portal.distribuce24.cz)
- Generated API credentials (`client_id` + `client_secret`)
- EAN number of your meter point

---

## Installation

### Via HACS (recommended)

1. Open **HACS** → **Integrations**
2. Click ⋮ → **Custom repositories**
3. Add URL:
   ```
   https://github.com/blesk89/HomeAssistant-EGD-distribuce24
   ```
   Category: **Integration**
4. Find **EGD Power Data** and click **Download**
5. Restart Home Assistant

### Manual installation

1. Download the latest release from [GitHub](https://github.com/blesk89/HomeAssistant-EGD-distribuce24/releases)
2. Copy the `custom_components/egdczpowerdata` folder to your `/config/custom_components/` directory
3. Restart Home Assistant

---

## Getting API credentials

1. Log in at [portal.distribuce24.cz](https://portal.distribuce24.cz)
2. Go to **Správa účtu** → **Vzdálený přístup OPENAPI**
3. Click **VYGENEROVAT CLIENT_ID A CLIENT_SECRET**
4. Note your `client_id`, `client_secret` and EAN number

> ⚠️ The access token is valid until midnight of the day it was generated. The integration handles token refresh automatically.

---

## Configuration

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: egdczpowerdata
    client_id: YOUR_CLIENT_ID
    client_secret: YOUR_CLIENT_SECRET
    ean: YOUR_EAN
    days: 1  # number of days back (default: 1)
```

### Multiple meter points

```yaml
sensor:
  - platform: egdczpowerdata
    client_id: YOUR_CLIENT_ID_1
    client_secret: YOUR_CLIENT_SECRET_1
    ean: YOUR_EAN_1
    days: 1

  - platform: egdczpowerdata
    client_id: YOUR_CLIENT_ID_2
    client_secret: YOUR_CLIENT_SECRET_2
    ean: YOUR_EAN_2
    days: 1
```

### Configuration options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `client_id` | ✅ | — | API client ID from distribuce24.cz |
| `client_secret` | ✅ | — | API client secret from distribuce24.cz |
| `ean` | ✅ | — | EAN number of the meter point |
| `days` | ❌ | `1` | Number of days back to fetch |

---

## Entities

After restart, the following entities will be created:

| Entity | Unit | Description |
|--------|------|-------------|
| `sensor.egddistribuce_<EAN>_<days>_icc1` | kWh | Electricity consumption |
| `sensor.egddistribuce_<EAN>_<days>_isc1` | kWh | Solar production / grid feed-in |
| `sensor.egddistribuce_status_<EAN>_<days>` | — | Last update status |

---

## Energy Dashboard

This integration is fully compatible with the Home Assistant **Energy Dashboard**.

Go to **Settings → Energy** and add:
- `sensor.egddistribuce_<EAN>_<days>_icc1` as **Grid consumption**
- `sensor.egddistribuce_<EAN>_<days>_isc1` as **Return to grid** (if you have solar)

---

## Data update frequency

- Data is fetched **once per day** (24-hour throttle)
- EG.D publishes previous day data from approximately **10:00**
- Avoid scheduling downloads on exact hours (e.g. 16:00) — EG.D servers are heavily loaded at full hours

---

## Troubleshooting

Check the log file at `/config/egddistribuce.log` for detailed debug information.

| Error | Cause | Solution |
|-------|-------|----------|
| `V požadovaném období nemáte oprávnění` | EAN not assigned to API account | Add EAN in portal.distribuce24.cz |
| `Error retrieving access token` | Invalid credentials | Check client_id and client_secret |
| Sensor shows `unknown` | Data not yet published | Wait until after 10:00 next day |

---

## Supported meter types

| Type | Description | Supported |
|------|-------------|-----------|
| A | Direct measurement (large consumers, FVE) | ✅ |
| B | Indirect measurement (SME, medium consumers) | ✅ |
| C | Standard household meter | ❌ |

---

## Changelog

### v0.2.0
- Fixed polling interval (15 min → 24 hours)
- Secure token handling (no plaintext in logs)
- Added rotating log file (max 1 MB, 3 backups)
- Added `state_class` for Energy dashboard compatibility
- Fixed bare `except` clause
- Added HACS support

---

## Credits

Based on original work by [ondrejvysek/HomeAssistant-EGD-PowerData](https://github.com/ondrejvysek/HomeAssistant-EGD-PowerData).

---

## License

MIT License — see [LICENSE](LICENSE) file for details.
