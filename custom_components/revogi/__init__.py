"""Petoneer Custom Component"""

from h11 import Data
from .const import(
    DOMAIN,
    CONF_SERIAL,
)

from .petoneer import Petoneer

import logging
from datetime import timedelta
import async_timeout
import asyncio

from homeassistant import core
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator 
from homeassistant.helpers.discovery import async_load_platform


PLATFORMS = ['sensor', 'switch']

""" CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_SERIAL): cv.string
            }
        )
    },
    # The full HA configurations gets passed to `async_setup` so we need to allow
    # extra keys.
    extra=vol.ALLOW_EXTRA,
)
 """

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: core.HomeAssistant, entry: ConfigEntry)-> bool:
    """Set up the platform.
    @NOTE: `config` is the full dict from `configuration.yaml`.
    :returns: A boolean to indicate that initialization was successful.
    """

    username = entry.options[CONF_USERNAME]
    password = entry.options[CONF_PASSWORD]
    serial   = entry.options[CONF_SERIAL]

    conf = {
        CONF_USERNAME: username,
        CONF_PASSWORD: password,
        CONF_SERIAL: serial
    }

    pet = Petoneer()
    await pet.auth(username, password)
    
    coordinator = PetoneerCoordinator(hass, pet, serial)

    await coordinator.async_refresh()
    _LOGGER.debug("Coordinator has synced")
    
    hass.data[DOMAIN] = {
        "conf": conf,
        "coordinator": coordinator,
    }

    _LOGGER.debug("Load Sensor")
    hass.async_create_task(async_load_platform(hass, "sensor", DOMAIN, {}, conf))
    _LOGGER.debug("Load Switch")
    hass.async_create_task(async_load_platform(hass, "switch", DOMAIN, {}, conf)) 

    return True

    

class PetoneerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, pet_api, serial):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.pet_api = pet_api
        #self.hass = hass
        self.serial = serial

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        async with async_timeout.timeout(10):
            return await self.pet_api.fetch_data(self.serial)
        #try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
        #    async with async_timeout.timeout(10):
        #        return await self.pet_api.fetch_data(hass.data[DOMAIN]["conf"][CONF_SERIAL])
        #except ApiAuthError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #    raise ConfigEntryAuthFailed from err
        #except ApiError as err:
        #    raise UpdateFailed(f"Error communicating with API: {err}")




