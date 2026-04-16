import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_EAN, CONF_DAYS


class EGDCZPowerDataConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Vrátí options flow handler — umožňuje změnu nastavení po první konfiguraci."""
        return EGDCZPowerDataOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_EAN])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"EGD Power Data ({user_input[CONF_EAN]})",
                data=user_input,
            )

        data_schema = vol.Schema({
            vol.Required(CONF_CLIENT_ID): str,
            vol.Required(CONF_CLIENT_SECRET): str,
            vol.Required(CONF_EAN): str,
            vol.Optional(CONF_DAYS, default=7): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )


class EGDCZPowerDataOptionsFlow(config_entries.OptionsFlow):
    """Options flow — umožňuje uživateli změnit počet dní a spustit historický backfill.

    Nastavením vyššího počtu dní (např. 365) se při příštím automatickém
    nebo ručním obnovení stáhnou a importují historická data za celé období.
    Data se stahují po blocích 30 dní, takže limit API není překročen.
    """

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Zobrazí formulář pro změnu nastavení."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Aktuální hodnota days — z options nebo z původní konfigurace
        current_days = self._config_entry.options.get(
            CONF_DAYS,
            self._config_entry.data.get(CONF_DAYS, 7),
        )

        data_schema = vol.Schema({
            vol.Optional(CONF_DAYS, default=current_days): int,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
