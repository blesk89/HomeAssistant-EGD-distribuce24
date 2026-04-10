"""Testy pro EGD Power Data senzory."""
import pytest
from unittest.mock import patch, MagicMock
import requests

from custom_components.egdczpowerdata.sensor import (
    EGDPowerDataConsumptionSensor,
    EGDPowerDataProductionSensor,
    EGDPowerDataStatusSensor,
)
from custom_components.egdczpowerdata.const import TOKEN_URL, DATA_URL
from tests.conftest import CONFIG, MOCK_TOKEN, MOCK_DATA_RESPONSE, MOCK_TOKEN_RESPONSE


# ─── Pomocné funkce ───────────────────────────────────────────────

def make_consumption_sensor(mock_api):
    """Vytvoří instanci senzoru spotřeby s mockovaným API."""
    hass = MagicMock()
    return EGDPowerDataConsumptionSensor(
        hass,
        CONFIG["client_id"],
        CONFIG["client_secret"],
        CONFIG["ean"],
        CONFIG["days"],
    )


def make_production_sensor(mock_api):
    """Vytvoří instanci senzoru výroby s mockovaným API."""
    hass = MagicMock()
    return EGDPowerDataProductionSensor(
        hass,
        CONFIG["client_id"],
        CONFIG["client_secret"],
        CONFIG["ean"],
        CONFIG["days"],
    )


# ─── Testy tokenu ─────────────────────────────────────────────────

class TestAccessToken:
    def test_token_je_ziskan(self, mock_api):
        """Ověří, že se token úspěšně získá z API."""
        sensor = make_consumption_sensor(mock_api)
        token = sensor._get_access_token()
        assert token == MOCK_TOKEN

    def test_token_request_obsahuje_spravne_parametry(self, mock_api):
        """Ověří, že požadavek na token obsahuje správné parametry."""
        sensor = make_consumption_sensor(mock_api)
        sensor._get_access_token()
        call_kwargs = mock_api["token"].call_args
        data = call_kwargs[1]["data"] if "data" in call_kwargs[1] else call_kwargs[0][1]
        assert data["grant_type"] == "client_credentials"
        assert data["client_id"] == CONFIG["client_id"]
        assert data["client_secret"] == CONFIG["client_secret"]
        assert data["scope"] == "namerena_data_openapi"

    def test_token_request_na_spravnou_url(self, mock_api):
        """Ověří, že se token získává ze správné URL."""
        sensor = make_consumption_sensor(mock_api)
        sensor._get_access_token()
        call_args = mock_api["token"].call_args
        url = call_args[0][0]
        assert url == TOKEN_URL

    def test_chyba_pri_ziskani_tokenu(self, mock_token_request, mock_data_request):
        """Ověří, že se chyba při získání tokenu správně propaguje."""
        mock_token_request.return_value.raise_for_status.side_effect = (
            requests.exceptions.RequestException("Chyba autentizace")
        )
        hass = MagicMock()
        sensor = EGDPowerDataConsumptionSensor(
            hass, CONFIG["client_id"], CONFIG["client_secret"], CONFIG["ean"], CONFIG["days"]
        )
        assert sensor.state is None


# ─── Testy senzoru spotřeby (ICC1) ───────────────────────────────

class TestConsumptionSensor:
    def test_stav_senzoru_je_spravny(self, mock_api):
        """Ověří, že senzor vrátí správnou hodnotu spotřeby v kWh."""
        sensor = make_consumption_sensor(mock_api)
        # 4 hodnoty: 100+200+300+400 = 1000, děleno 4 = 250 kWh
        assert sensor.state == 250.0

    def test_jednotka_je_kwh(self, mock_api):
        """Ověří, že senzor vrátí kWh."""
        sensor = make_consumption_sensor(mock_api)
        assert sensor.unit_of_measurement == "kWh"

    def test_device_class_je_energy(self, mock_api):
        """Ověří, že device_class je energy."""
        from homeassistant.components.sensor import SensorDeviceClass
        sensor = make_consumption_sensor(mock_api)
        assert sensor.device_class == SensorDeviceClass.ENERGY

    def test_unique_id_obsahuje_ean(self, mock_api):
        """Ověří, že unique_id obsahuje EAN."""
        sensor = make_consumption_sensor(mock_api)
        assert CONFIG["ean"] in sensor.unique_id

    def test_profil_je_icc1(self, mock_api):
        """Ověří, že senzor spotřeby používá profil ICC1."""
        sensor = make_consumption_sensor(mock_api)
        assert sensor.profile == "ICC1"

    def test_atributy_obsahuji_casove_razitko(self, mock_api):
        """Ověří, že extra_state_attributes obsahují časová razítka."""
        sensor = make_consumption_sensor(mock_api)
        attrs = sensor.extra_state_attributes
        assert "stime" in attrs
        assert "etime" in attrs
        assert "local_stime" in attrs
        assert "local_etime" in attrs


# ─── Testy senzoru výroby (ISC1) ─────────────────────────────────

class TestProductionSensor:
    def test_profil_je_isc1(self, mock_api):
        """Ověří, že senzor výroby používá profil ISC1."""
        sensor = make_production_sensor(mock_api)
        assert sensor.profile == "ISC1"

    def test_stav_senzoru_je_spravny(self, mock_api):
        """Ověří, že senzor výroby vrátí správnou hodnotu."""
        sensor = make_production_sensor(mock_api)
        assert sensor.state == 250.0

    def test_unique_id_liší_se_od_spotřeby(self, mock_api):
        """Ověří, že senzory spotřeby a výroby mají různé unique_id."""
        consumption = make_consumption_sensor(mock_api)
        production = make_production_sensor(mock_api)
        assert consumption.unique_id != production.unique_id


# ─── Testy prázdných a chybných dat ──────────────────────────────

class TestChybnaData:
    def test_prazdna_data_vraci_nulu(self, mock_token_request, mock_data_request):
        """Ověří, že prázdná odpověď API vrátí hodnotu 0."""
        mock_data_request.return_value.json.return_value = [{"data": []}]
        hass = MagicMock()
        sensor = EGDPowerDataConsumptionSensor(
            hass, CONFIG["client_id"], CONFIG["client_secret"], CONFIG["ean"], CONFIG["days"]
        )
        assert sensor.state == 0

    def test_chybna_odpoved_api_vraci_none(self, mock_token_request, mock_data_request):
        """Ověří, že chyba API vrátí None."""
        mock_data_request.return_value.raise_for_status.side_effect = (
            requests.exceptions.RequestException("Server error")
        )
        hass = MagicMock()
        sensor = EGDPowerDataConsumptionSensor(
            hass, CONFIG["client_id"], CONFIG["client_secret"], CONFIG["ean"], CONFIG["days"]
        )
        assert sensor.state is None

    def test_chybejici_ean_neprovede_update(self, mock_api):
        """Ověří, že prázdný EAN přeskočí aktualizaci."""
        hass = MagicMock()
        sensor = EGDPowerDataConsumptionSensor(
            hass, CONFIG["client_id"], CONFIG["client_secret"], "", CONFIG["days"]
        )
        assert sensor.state is None


# ─── Testy výpočtu hodnot ────────────────────────────────────────

class TestVypocetHodnot:
    def test_hodnoty_se_deli_ctyrmi(self, mock_token_request, mock_data_request):
        """Ověří, že hodnoty kW jsou správně převedeny na kWh (děleno 4)."""
        mock_data_request.return_value.json.return_value = [
            {"data": [{"value": 400, "status": "IU012"}]}
        ]
        hass = MagicMock()
        sensor = EGDPowerDataConsumptionSensor(
            hass, CONFIG["client_id"], CONFIG["client_secret"], CONFIG["ean"], CONFIG["days"]
        )
        # 400 / 4 = 100 kWh
        assert sensor.state == 100.0

    def test_soucet_vsech_hodnot(self, mock_token_request, mock_data_request):
        """Ověří, že se sečtou všechny hodnoty před dělením."""
        mock_data_request.return_value.json.return_value = [
            {
                "data": [
                    {"value": 100, "status": "IU012"},
                    {"value": 100, "status": "IU012"},
                    {"value": 100, "status": "IU012"},
                    {"value": 100, "status": "IU012"},
                ]
            }
        ]
        hass = MagicMock()
        sensor = EGDPowerDataConsumptionSensor(
            hass, CONFIG["client_id"], CONFIG["client_secret"], CONFIG["ean"], CONFIG["days"]
        )
        # (100+100+100+100) / 4 = 100 kWh
        assert sensor.state == 100.0
