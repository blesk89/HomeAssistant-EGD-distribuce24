# Changelog

## [0.5.1]

### Fixed
- Oprava blokujícího `self.update()` v konstruktorech senzorů
- `async_import_statistics` → `async_add_external_statistics` (HA 2026.4)
- Agregace 15min hodnot do hodinových bucketů
- Přidáno `mean_type=StatisticMeanType.NONE` do `StatisticMetaData`
- Odstraněno `update_before_add=True` z `add_entities`

---

## [0.4.0]

### Added
- Import 15minutových statistik do HA recorder přes `async_import_statistics`
  - Statistiky jsou dostupné jako `egdczpowerdata:egddistribuce_{ean}_{days}_{profile}`
  - Energy dashboard zobrazuje 15minutové rozlišení spotřeby/výroby
  - Kumulativní součet navazuje na předchozí statistiky (bezpečný upsert)
- Nová async metoda `_import_statistics` v `EGDPowerDataSensor`

### Changed
- `manifest.json`: verze `0.3.0` → `0.4.0`
- `sensor.py`: `_get_data` nyní extrahuje raw 15min hodnoty a spouští import statistik

---

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
