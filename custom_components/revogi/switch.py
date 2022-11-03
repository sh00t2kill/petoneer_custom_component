import logging
import urllib.parse

import aiohttp
import asyncio
import json
import hashlib

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
import async_timeout
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import *
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import(
    DEFAULT_NAME,
    DOMAIN,
    ATTR_LEVEL,
    ATTR_TDS ,
    ATTR_LED,
    ATTR_LEDMODE,
    ATTR_SWITCH,
    CONF_SERIAL,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):
    """Setup the switch platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([PetoneerSwitch(coordinator, hass)], True)

class PetoneerSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator: DataUpdateCoordinator, hass):
        super().__init__(coordinator)
        self._state = None
        self._id = hass.data[DOMAIN]["conf"][CONF_SERIAL]#id
        self.entity_id = DOMAIN + "." + self._id
        self.pet_api = coordinator.pet_api
        self.coordinator = coordinator

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._id

    def device_info(self):
        return {
            "name": DEFAULT_NAME,
            "serial": self._id
        }

    @property
    def name(self):
        return f"Petoneer {self._id}"

    async def async_turn_on(self, **kwargs):
        """Turn the entity on"""
        attributes = await self.pet_api.turn_on(self._id)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off"""
        attributes = await self.pet_api.turn_off(self._id)
        await self.coordinator.async_request_refresh()

    @property
    def state(self):
        attributes = self.coordinator.data#.values()
        self._state = attributes['switch']
        state = "off"
        if (self._state == 1):
            state = "on"
        return state

    @property
    def is_on(self):
        return self._state == 1
