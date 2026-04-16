# __init__.py
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

DOMAIN = "egdczpowerdata"

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    # Při změně options (např. nový počet dní) se integrace automaticky restartuje
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Znovu načte integraci po uložení nových options."""
    await hass.config_entries.async_reload(entry.entry_id)
