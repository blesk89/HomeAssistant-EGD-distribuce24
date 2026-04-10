# EGD Power Data — Home Assistant integrace

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/blesk89/HomeAssistant-EGD-distribuce24.svg)](https://github.com/blesk89/HomeAssistant-EGD-distribuce24/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Home Assistant integrace pro stahování dat chytrého elektroměru z portálu [EG.D distribuce24](https://portal.distribuce24.cz) přes OpenAPI.

Podporuje stahování **spotřeby elektřiny** a **výroby z fotovoltaiky** v 15minutových intervalech, plně kompatibilní s HA Energy dashboardem.

---

## Funkce

- ⚡ Spotřeba elektřiny (kWh) — profil ICC1
- ☀️ Výroba elektřiny / dodávka do sítě (kWh) — profil ISC1
- 📊 Plná podpora HA Energy dashboardu
- 🔄 Automatická denní aktualizace (data publikuje EG.D od 10:00 za předchozí den)
- 📝 Rotující log soubor (max 1 MB, 3 zálohy)
- 🔒 Bezpečné zacházení s tokenem (žádné plaintext logování)

---

## Požadavky

- Chytrý elektroměr typu **A nebo B** (nepodporuje typ C — běžné domácí elektroměry bez dálkového odečtu)
- Přístup na portál [distribuce24.cz](https://portal.distribuce24.cz)
- Vygenerované API přihlašovací údaje (`client_id` + `client_secret`)
- EAN číslo odběrného místa

---

## Instalace

### Přes HACS (doporučeno)

1. Otevři **HACS** → **Integrace**
2. Klikni na ⋮ → **Vlastní repozitáře**
3. Přidej URL:
   ```
   https://github.com/blesk89/HomeAssistant-EGD-distribuce24
   ```
   Kategorie: **Integrace**
4. Najdi **EGD Power Data** a klikni na **Stáhnout**
5. Restartuj Home Assistant

### Ruční instalace

1. Stáhni nejnovější verzi z [GitHub releases](https://github.com/blesk89/HomeAssistant-EGD-distribuce24/releases)
2. Zkopíruj složku `custom_components/egdczpowerdata` do adresáře `/config/custom_components/`
3. Restartuj Home Assistant

---

## Získání API přihlašovacích údajů

1. Přihlas se na [portal.distribuce24.cz](https://portal.distribuce24.cz)
2. Přejdi do **Správa účtu** → **Vzdálený přístup OPENAPI**
3. Klikni na **VYGENEROVAT CLIENT_ID A CLIENT_SECRET**
4. Poznamenej si `client_id`, `client_secret` a EAN číslo svého odběrného místa

> ⚠️ Access token je platný do půlnoci dne, kdy byl vygenerován. Integrace obnovuje token automaticky.

---

## Konfigurace

Přidej do souboru `configuration.yaml`:

```yaml
sensor:
  - platform: egdczpowerdata
    client_id: TVUJ_CLIENT_ID
    client_secret: TVUJ_CLIENT_SECRET
    ean: TVUJ_EAN
    days: 1  # počet dní zpětně (výchozí: 1)
```

### Více odběrných míst

```yaml
sensor:
  - platform: egdczpowerdata
    client_id: TVUJ_CLIENT_ID_1
    client_secret: TVUJ_CLIENT_SECRET_1
    ean: TVUJ_EAN_1
    days: 1

  - platform: egdczpowerdata
    client_id: TVUJ_CLIENT_ID_2
    client_secret: TVUJ_CLIENT_SECRET_2
    ean: TVUJ_EAN_2
    days: 1
```

### Parametry konfigurace

| Parametr | Povinný | Výchozí | Popis |
|----------|---------|---------|-------|
| `client_id` | ✅ | — | API client ID z distribuce24.cz |
| `client_secret` | ✅ | — | API client secret z distribuce24.cz |
| `ean` | ✅ | — | EAN číslo odběrného místa |
| `days` | ❌ | `1` | Počet dní zpětně |

---

## Senzory

Po restartu budou vytvořeny následující entity:

| Entita | Jednotka | Popis |
|--------|----------|-------|
| `sensor.egddistribuce_<EAN>_<days>_icc1` | kWh | Spotřeba elektřiny |
| `sensor.egddistribuce_<EAN>_<days>_isc1` | kWh | Výroba / dodávka do sítě |
| `sensor.egddistribuce_status_<EAN>_<days>` | — | Stav poslední aktualizace |

---

## Energy Dashboard

Integrace je plně kompatibilní s **Energy Dashboardem** Home Assistantu.

Přejdi do **Nastavení → Energie** a přidej:
- `sensor.egddistribuce_<EAN>_<days>_icc1` jako **Spotřeba ze sítě**
- `sensor.egddistribuce_<EAN>_<days>_isc1` jako **Dodávka do sítě** (pokud máš FVE)

---

## Frekvence aktualizace dat

- Data se stahují **jednou denně** (24hodinový throttle)
- EG.D publikuje data za předchozí den přibližně od **10:00**
- Nedoporučuje se plánovat stahování na celé hodiny (např. 16:00) — servery EG.D jsou v tyto časy přetížené

---

## Řešení problémů

Podrobné informace najdeš v log souboru `/config/egddistribuce.log`.

| Chyba | Příčina | Řešení |
|-------|---------|--------|
| `V požadovaném období nemáte oprávnění` | EAN není přiřazen k API účtu | Přidej EAN na portal.distribuce24.cz |
| `Error retrieving access token` | Neplatné přihlašovací údaje | Zkontroluj client_id a client_secret |
| Senzor zobrazuje `unknown` | Data ještě nejsou dostupná | Počkej do 10:00 následujícího dne |

---

## Podporované typy elektroměrů

| Typ | Popis | Podpora |
|-----|-------|---------|
| A | Přímé měření (velcí odběratelé, FVE) | ✅ |
| B | Nepřímé měření (SME, střední odběratelé) | ✅ |
| C | Běžný domácí elektroměr | ❌ |

---

## Spuštění testů

```bash
pip install -r requirements_test.txt
pytest tests/
```

---

## Changelog

### v0.2.0
- Opraven interval pollingu (15 min → 24 hodin)
- Bezpečné zacházení s tokenem (žádné plaintext logování)
- Přidán rotující log soubor (max 1 MB, 3 zálohy)
- Přidán `state_class` pro kompatibilitu s Energy dashboardem
- Opravena holá klauzule `except`
- Přidána podpora HACS

---

## Poděkování

Vychází z původní práce [ondrejvysek/HomeAssistant-EGD-PowerData](https://github.com/ondrejvysek/HomeAssistant-EGD-PowerData).

---

## Licence

MIT licence — viz soubor [LICENSE](LICENSE).
