# Changelog

## [0.8.1]

### Fixed
- Oprava parsování odpovědi EGD API po změně formátu na straně serveru
  - EGD API změnilo formát odpovědi z listu `[{...}]` na dict `{...}`
  - Kód v `_fetch_all_chunks` používal `data[0]['data']`, což způsobovalo `KeyError`
  - Chyba byla tiše zachycena → prázdná data → integrace hlásila "EGD returned 0" pro všechny dny
  - Opraveno na `data['data']` — správné čtení klíče ze slovníku

### Changed
- `manifest.json`: verze `0.8.0` → `0.8.1`

---

## [0.8.0]

### Fixed
- Oprava poškozené kumulativní sumy statistik při `days > 1`
  - Při každém denním běhu se přepisovalo celé okno (`days` dní) s kumulativní sumou začínající od 0
  - Podmínka `if entry_start_dt < sorted_hours[0]` nikdy nebyla splněna (poslední DB záznam byl vždy uvnitř okna)
  - Výsledek: kumulativní součet se každý den resetoval → špatný graf v Energy dashboardu
- **Nová logika** v `_import_statistics`: importují se pouze hodiny **po posledním záznamu v DB**
  - Kumulativní součet vždy správně navazuje na existující data
  - Historická data se nepřepisují
  - Zpětný import (backfill) funguje správně při prázdné DB nebo vysokém `days`

### Changed
- `manifest.json`: verze `0.7.0` → `0.8.0`

---

## [0.7.0]

### Fixed
- EGD API vrací 0 pro celý rozsah dat, pokud rozsah zahrnuje dny bez publikovaných dat
  - Nová retry logika v `_get_data`: pokud API vrátí 0, posune se celé okno (stime i etime) o 1 den zpět
  - Max 5 pokusů — každý pokus posune okno o 1 den starší
  - Zajišťuje robustní chování i při EGD zpoždění > 1 den

### Changed
- Výchozí hodnota `days` zvýšena z 1 na 5 (zachytí data i při 2–3 denním zpoždění EGD API)
- `manifest.json`: verze `0.6.0` → `0.7.0`

---

## [0.6.0]

### Added
- Podpora načítání dat za libovolně dlouhé historické období (backfill)
  - API požadavky se automaticky dělí do bloků po 30 dnech (limit pageSize=3000)
  - Stačí nastavit vyšší hodnotu parametru `days` (např. 365 pro celý rok)
  - Kumulativní součet statistik správně navazuje na existující data v databázi
- Nová metoda `_fetch_all_chunks` — stahuje data po blocích a vrací sloučený hodinový dict
- Nová třídní konstanta `_CHUNK_DAYS = 30` — velikost jednoho bloku

### Changed
- `_get_data`: místo jednoho API volání nyní volá `_fetch_all_chunks`
- `_import_statistics`: přijímá `dict {hour_utc: kWh}` místo flat listu hodnot a počátečního timestampu
- `sensor.py`: `days` se čte přednostně z `entry.options` (umožňuje změnu přes UI bez přeinstalace)
- `manifest.json`: verze `0.5.1` → `0.6.0`
- Výchozí hodnota `days` změněna z 1 na 7

### UI — Options Flow (Konfigurovat)
- Uživatel může po nastavení integrace kdykoli změnit `Počet dní zpětně` přes tlačítko **Konfigurovat**
- Formulář obsahuje popis: nastavení vyššího počtu dní (např. 365) spustí jednorázový historický import
- Po uložení se integrace automaticky restartuje a při příštím obnovení stáhne historická data
- `__init__.py`: přidán `update_listener` → reload při změně options
- `config_flow.py`: přidán `EGDCZPowerDataOptionsFlow`
- `strings.json` + `translations/cs.json`: přidána sekce `options` s popisky polí

---

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
