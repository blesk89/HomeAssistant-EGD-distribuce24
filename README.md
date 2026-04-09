# HomeAssistant EGD distribuce24

Home Assistant integrace pro stahování 15-minutových dat elektroměru z portálu [EG.D distribuce](https://portal.distribuce24.cz) přes OpenAPI.

## Funkce

- Spotřeba elektřiny (kWh) za zvolené období
- Výroba elektřiny (kWh) za zvolené období (fotovoltaika)
- Stavový senzor poslední aktualizace
- Plná podpora HA Energy dashboardu

## Požadavky

- Smart elektroměr typu A nebo B (nepodporuje typ C — běžné domácí elektroměry)
- Přístup na portál [distribuce24.cz](https://portal.distribuce24.cz)
- Vygenerované API klíče (client_id + client_secret)

## Instalace přes HACS

1. HACS → Custom repositories → přidej URL:
   ```
   https://github.com/blesk89/HomeAssistant-EGD-distribuce24
   ```
2. Kategorie: **Integration**
3. Nainstaluj a restartuj HA

## Ruční instalace

Zkopíruj složku `custom_components/egdczpowerdata` do `/config/custom_components/` a restartuj HA.

## Získání API klíčů

1. Přihlas se na [portal.distribuce24.cz](https://portal.distribuce24.cz)
2. Správa účtu → **Vzdálený přístup OPENAPI**
3. Vygeneruj `client_id` a `client_secret`

## Konfigurace

Přidej do `configuration.yaml`:

```yaml
sensor:
  - platform: egdczpowerdata
    client_id: TVUJ_CLIENT_ID
    client_secret: TVUJ_CLIENT_SECRET
    ean: TVUJ_EAN
    days: 1  # počet dní zpětně (výchozí: 1)
```

## Senzory

| Entita | Popis |
|---|---|
| `sensor.egddistribuce_<EAN>_<days>_icc1` | Spotřeba (kWh) |
| `sensor.egddistribuce_<EAN>_<days>_isc1` | Výroba (kWh) |
| `sensor.egddistribuce_status_<EAN>_<days>` | Stav poslední aktualizace |

## Poznámky

- Data se aktualizují **1× denně** (EG.D publikuje data od 10:00 za předchozí den)
- Funguje pouze pro měřicí typ A nebo B (chytré elektroměry, nepřímé měření, FVE)

## Změny oproti původní verzi

- Opraven interval pollingu (15 min → 24 hodin)
- Access token se neloguje v plaintext
- Rotující log soubor (max 1 MB)
- Přidán `state_class` pro Energy dashboard
- Opravena holá `except` klauzule

## Původní autor

Původní integrace: [ondrejvysek/HomeAssistant-EGD-PowerData](https://github.com/ondrejvysek/HomeAssistant-EGD-PowerData)
