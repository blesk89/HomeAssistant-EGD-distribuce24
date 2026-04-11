import logging
import logging.handlers
import datetime
from datetime import timedelta
from datetime import datetime as dt
from zoneinfo import ZoneInfo
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfEnergy
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import Throttle
from homeassistant.helpers.entity_component import async_update_entity
from homeassistant.core import HomeAssistant
from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.models import StatisticMeanType
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
)
from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_EAN, CONF_DAYS, TOKEN_URL, DATA_URL

PRAGUE_TZ = ZoneInfo('Europe/Prague')
UTC_TZ = ZoneInfo('UTC')

# Create a custom logger for the component
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# Rotating file handler — max 1 MB, 3 zálohy
file_handler = logging.handlers.RotatingFileHandler(
    '/config/egddistribuce.log',
    maxBytes=1_000_000,
    backupCount=3
)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
_LOGGER.addHandler(file_handler)

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=24)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CLIENT_ID): cv.string,
    vol.Required(CONF_CLIENT_SECRET): cv.string,
    vol.Required(CONF_EAN): cv.string,
    vol.Optional(CONF_DAYS, default=1): cv.positive_int,
})

async def async_setup_entry(hass, entry, async_add_entities):
    client_id = entry.data[CONF_CLIENT_ID]
    client_secret = entry.data[CONF_CLIENT_SECRET]
    ean = entry.data[CONF_EAN]
    days = entry.data.get(CONF_DAYS, 1)

    async_add_entities([
        EGDPowerDataStatusSensor(hass, client_id, client_secret, ean, days),
        EGDPowerDataConsumptionSensor(hass, client_id, client_secret, ean, days),
        EGDPowerDataProductionSensor(hass, client_id, client_secret, ean, days),
    ])


def setup_platform(hass, config, add_entities, discovery_info=None):
    client_id = config[CONF_CLIENT_ID]
    client_secret = config[CONF_CLIENT_SECRET]
    ean = config[CONF_EAN]
    days = config[CONF_DAYS]

    status_sensor = EGDPowerDataStatusSensor(hass, client_id, client_secret, ean, days)
    consumption_sensor = EGDPowerDataConsumptionSensor(hass, client_id, client_secret, ean, days)
    production_sensor = EGDPowerDataProductionSensor(hass, client_id, client_secret, ean, days)

    add_entities([status_sensor, consumption_sensor, production_sensor])

class EGDPowerDataSensor(Entity):
    def __init__(self, hass, client_id, client_secret, ean, days, profile):
        self.hass = hass
        self.client_id = client_id
        self.client_secret = client_secret
        self.ean = ean
        self.days = days
        self.profile = profile
        self._state = None
        self._attributes = {}
        self._unique_id = f"egddistribuce_{ean}_{days}_{profile.lower()}"
        self.entity_id = f"sensor.egddistribuce_{ean}_{days}_{profile.lower()}"
        _LOGGER.debug(f"Initialized EGDPowerDataSensor with EAN: {self.ean}, Profile: {self.profile}")

    @property
    def name(self):
        return f"EGD Power Data Sensor {self.ean} {self.days} {self.profile}"

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def extra_state_attributes(self):
        return self._attributes

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        if not self.ean:
            _LOGGER.warning("EAN is not set. Skipping update.")
            return

        _LOGGER.debug(f"Updating EGD Power Data Sensor for EAN: {self.ean}, Profile: {self.profile}")
        try:
            token = await self._get_access_token()
            await self._get_data(token)
        except Exception as e:
            _LOGGER.error(f"Error updating sensor: {e}")

    async def _get_access_token(self):
        _LOGGER.debug("Retrieving access token")
        session = async_get_clientsession(self.hass)
        try:
            async with session.post(
                TOKEN_URL,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'scope': 'namerena_data_openapi'
                }
            ) as response:
                response.raise_for_status()
                data = await response.json()
                token = data.get('access_token')
                _LOGGER.debug("Access token retrieved successfully")
                return token
        except Exception as e:
            _LOGGER.error(f"Error retrieving access token: {e}")
            raise

    async def _get_data(self, token):
        _LOGGER.debug("Retrieving consumption/production data")

        local_stime = (datetime.datetime.now() - timedelta(days=self.days)).replace(hour=0, minute=0, second=0, microsecond=0)
        local_etime = (datetime.datetime.now() - timedelta(days=1)).replace(hour=23, minute=45, second=0, microsecond=0)

        local_stime = local_stime.replace(tzinfo=PRAGUE_TZ)
        local_etime = local_etime.replace(tzinfo=PRAGUE_TZ)

        utc_stime = local_stime.astimezone(UTC_TZ)
        utc_etime = local_etime.astimezone(UTC_TZ)

        headers = {
            'Authorization': f'Bearer {token}'
        }
        params = {
            'ean': self.ean,
            'profile': self.profile,
            'from': utc_stime.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'to': utc_etime.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'pageSize': 3000
        }

        session = async_get_clientsession(self.hass)
        try:
            _LOGGER.debug(f"Request params: {params}")
            _LOGGER.debug(f"Data URL: {DATA_URL}")
            async with session.get(DATA_URL, headers=headers, params=params) as response:
                _LOGGER.debug(f"Response status code: {response.status}")
                response.raise_for_status()
                data = await response.json()

            try:
                items = data[0]['data']
                values = [item['value'] for item in items]
                total_value = sum(values) / 4
            except (KeyError, IndexError, TypeError):
                total_value = 0
                values = []

            self._state = total_value
            self._attributes = {
                'stime': utc_stime.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                'etime': utc_etime.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                'local_stime': local_stime.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                'local_etime': local_etime.strftime('%Y-%m-%d %H:%M:%S %Z%z')
            }
            _LOGGER.debug(f"Total value: {total_value}")

            if values:
                await self._import_statistics(values, utc_stime)
        except Exception as e:
            _LOGGER.error(f"Error retrieving data: {e}")
            raise

    async def _import_statistics(self, values, start_time):
        statistic_id = f"egdczpowerdata:{self._unique_id}"

        last_sum = 0.0
        try:
            recorder = get_instance(self.hass)
            last_stats = await recorder.async_add_executor_job(
                get_last_statistics, self.hass, 1, statistic_id, True, {"sum"}
            )
            if last_stats and statistic_id in last_stats:
                entry = last_stats[statistic_id][0]
                if entry.get("sum") is not None:
                    entry_start = entry.get("start")
                    if isinstance(entry_start, (int, float)):
                        entry_start_dt = datetime.datetime.fromtimestamp(entry_start, tz=UTC_TZ)
                    else:
                        entry_start_dt = entry_start
                    if entry_start_dt < start_time:
                        last_sum = entry["sum"]
        except Exception as e:
            _LOGGER.warning(f"Could not get last statistics: {e}")

        # Aggregate 15-minute values into hourly buckets (4 intervals per hour)
        hourly_buckets: dict = {}
        interval_start = start_time
        for value in values:
            hour_start = interval_start.replace(minute=0, second=0, microsecond=0)
            hourly_buckets[hour_start] = hourly_buckets.get(hour_start, 0.0) + value / 4
            interval_start += timedelta(minutes=15)

        stats = []
        cumulative = last_sum
        for hour_start in sorted(hourly_buckets):
            kwh = hourly_buckets[hour_start]
            cumulative += kwh
            stats.append(StatisticData(start=hour_start, sum=cumulative, state=kwh))

        metadata = StatisticMetaData(
            has_mean=False,
            mean_type=StatisticMeanType.NONE,
            has_sum=True,
            name=f"EGD {self.profile} {self.ean}",
            source="egdczpowerdata",
            statistic_id=statistic_id,
            unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            unit_class="energy",
        )
        async_add_external_statistics(self.hass, metadata, stats)
        _LOGGER.debug(f"Imported {len(stats)} statistics for {statistic_id}")

class EGDPowerDataConsumptionSensor(EGDPowerDataSensor):
    def __init__(self, hass, client_id, client_secret, ean, days):
        super().__init__(hass, client_id, client_secret, ean, days, 'ICC1')

    @property
    def unit_of_measurement(self):
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def device_class(self):
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        return SensorStateClass.TOTAL_INCREASING

class EGDPowerDataProductionSensor(EGDPowerDataSensor):
    def __init__(self, hass, client_id, client_secret, ean, days):
        super().__init__(hass, client_id, client_secret, ean, days, 'ISC1')

    @property
    def unit_of_measurement(self):
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def device_class(self):
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        return SensorStateClass.TOTAL_INCREASING

class EGDPowerDataStatusSensor(Entity):
    def __init__(self, hass, client_id, client_secret, ean, days):
        self.hass = hass
        self.client_id = client_id
        self.client_secret = client_secret
        self.ean = ean
        self.days = days
        self._state = None
        self._attributes = {}
        self._unique_id = f"egddistribuce_status_{ean}_{days}"
        self.entity_id = f"sensor.egddistribuce_status_{ean}_{days}"
        _LOGGER.debug(f"Initialized EGDPowerDataStatusSensor with EAN: {self.ean}")

    @property
    def name(self):
        return f"EGD Power Data Status Sensor {self.ean} {self.days}"

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def extra_state_attributes(self):
        return self._attributes

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        _LOGGER.debug(f"Updating EGD Power Data Status Sensor for EAN: {self.ean}")
        try:
            await self._update_related_sensors()
            self._state = "updated"
        except Exception as e:
            _LOGGER.error(f"Error updating status sensor: {e}")

    async def _update_related_sensors(self):
        _LOGGER.debug(f"Updating related sensors for EAN: {self.ean}")
        for entity_id in [
            f"sensor.egddistribuce_{self.ean}_{self.days}_icc1",
            f"sensor.egddistribuce_{self.ean}_{self.days}_isc1"
        ]:
            try:
                await async_update_entity(self.hass, entity_id)
            except Exception:
                pass  # entity not yet registered during first initialization
