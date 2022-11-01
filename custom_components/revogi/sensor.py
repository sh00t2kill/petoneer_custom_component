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
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION

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

from .petoneer import Petoneer


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Required(CONF_SERIAL): cv.string
            }
        )
    }
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    serial = config.get(CONF_SERIAL)

    pet = Petoneer()
    await pet.auth(username, password)
    
    _LOGGER.debug("Attempting to add entities")
    async_add_entities(
        [
            PetoneerSensor(
                pet,
                serial
            )
        ]
    ) 

class PetoneerSensor(SensorEntity):

    def __init__(self, pet, id):
        super().__init__()
        self._pet = pet
        self._state = None
        self.id = id
        self.entity_id = DOMAIN + "." + self.id
        self.attrs = {}

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self.id

    def device_info(self):
        return {
            "name": DEFAULT_NAME,
            "serial": self.id
        }

    def name(self):
        return f"Petoneer {self.id}"


    @property
    def device_state_attributes(self):
        return self.attrs

    async def async_update(self):
        _LOGGER.debug("Updating attributes")
        attributes = await self._pet.get_device_details(self.id)
        _LOGGER.debug(f"Attributes: {attributes}")
        self.attrs = {
            ATTR_LEVEL: attributes['level'],
            ATTR_TDS: attributes['tds'],
            ATTR_LED: attributes['led'],
            ATTR_LEDMODE: attributes['ledmode'],
            ATTR_SWITCH: attributes['switch']
        }

        # set the overall state -- use the level value for this
        self._state = attributes['level']
        self.async_write_ha_state()

    def device_state_attributes(self):
        return self.attrs

    def state(self):
        return self._state