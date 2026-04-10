# Changelog

## [0.3.0]

### Added
- Podpora konfigurace přes uživatelské rozhraní (UI config flow)
  - Integraci lze nyní přidat přes Nastavení → Integrace → Přidat integraci → EGD Power Data
  - Formulář obsahuje pole: Client ID, Client Secret, EAN, Počet dní
  - Ochrana proti duplicitní konfiguraci stejného EAN
- Překlady UI formuláře (`strings.json`, `translations/cs.json`)

### Changed
- `manifest.json`: přidáno `"config_flow": true`, verze `0.2.0` → `0.3.0`
- `const.py`: přesunuta konstanta `CONF_DAYS` ze `sensor.py` do `const.py`
- `__init__.py`: přidány funkce `async_setup_entry` a `async_unload_entry`
- `sensor.py`: přidána funkce `async_setup_entry` pro podporu config entry

### Notes
- Stávající konfigurace přes `configuration.yaml` zůstává plně funkční (zpětná kompatibilita zachována)

---

## [0.2.0]

- Přidány senzory spotřeby (ICC1) a výroby (ISC1)
- Rotující log soubor (`/config/egddistribuce.log`)
- Throttle aktualizace 1× za 24 hodin

## [0.1.0]

- První verze integrace EGD Power Data
