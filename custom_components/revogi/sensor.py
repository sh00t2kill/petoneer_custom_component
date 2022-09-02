import logging
import urllib.parse

import requests
import json
import hashlib

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
#from homeassistant.components.sensor import PLATFORM_SCHEMA
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import(
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

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = hass.data[DOMAIN].get("config") or {}
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    pet = Petoneer()
    pet.auth(config[CONF_USERNAME], config[CONF_PASSWORD])
    fountain = PetoneerSensor(pet, config[CONF_SERIAL])
    async_add_entities(fountain, update_before_add=True)


class PetoneerSensor:
    def __init__(self, pet, id):
        super().__init__()
        self.pet = pet
        self.attrs: Dict[str, Any]
        self._state = None
        self.id = id
        
    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self.id

    @property
    def device_state_attributes(self):
        return self.attrs

    async def async_update(self):
        attributes = self.pet.get_device_details(self.id)
        self.attrs[ATTR_LEVEL] = attributes.level
        self.attrs[ATTR_TDS]   = attributes.tds
        self.attrs[ATTR_LED]   = attributes.led
        self.attrs[ATTR_LEDMODE] = attributes.ledmode
        self.attrs[ATTR_SWITCH] = attributes.switch

        # set the overall state -- use the level value for this
        self._state = attributes.level


