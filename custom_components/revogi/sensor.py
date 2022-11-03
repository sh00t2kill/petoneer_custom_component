import logging
#from tkinter import SE
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
from homeassistant.components.sensor import SensorEntity
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
    """Setup the sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([PetoneerSensor(coordinator, hass)], True)

class PetoneerSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator: DataUpdateCoordinator, hass):
        super().__init__(coordinator)
        self._state = None
        self._id = hass.data[DOMAIN]["conf"][CONF_SERIAL]
        self.entity_id = DOMAIN + "." + self._id
        self._attrs = {}

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

    @property
    def extra_state_attributes(self):
        return self._attrs

    @property
    def state(self):
        
        attributes = self.coordinator.data#.values()
        _LOGGER.debug(f"Sensor state: {attributes}")
        self._attrs = {
            ATTR_LEVEL: attributes['level'],
            ATTR_TDS: attributes['tds'],
            ATTR_LED: attributes['led'],
            ATTR_LEDMODE: attributes['ledmode'],
            ATTR_SWITCH: attributes['switch']
        }

        self._state = attributes['level']

        return self._state
