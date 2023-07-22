"""Petoneer Custom Component"""

import asyncio
import logging
from datetime import timedelta

import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from h11 import Data
from homeassistant import core
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)

from .const import CONF_SERIAL, DOMAIN
from .petoneer import Petoneer

PLATFORMS = ['sensor', 'switch', 'binary_sensor']

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

    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("Coordinator has synced")

    hass.data[DOMAIN] = {
        "conf": conf,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a component config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class PetoneerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, pet_api, serial):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.pet_api = pet_api
        self.serial = serial

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(10):
                return await self.pet_api.fetch_data(self.serial)
        except ApiAuthError as err:
            # Raising ConfigEntryAuthFailed will cancel future updates
            # and start a config flow with SOURCE_REAUTH (async_step_reauth)
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    def get_device(self):
        return DeviceInfo(
            identifiers={
                (DOMAIN, self.serial)
            },
            name=f"Water Fountain {self.serial}",
            manufacturer="Petoneer",
            model="Fresco Pro",
        )
