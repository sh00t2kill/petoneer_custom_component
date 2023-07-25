import asyncio
import hashlib
import json
import logging
import urllib.parse

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import *
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from .const import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass, config, async_add_entities, discovery_info=None
):
    """Setup the sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([PetoneerSensor(coordinator, hass)], True)
    async_add_entities([PetoneerSensor(coordinator=coordinator, hass=hass, name="TDS", data_attribute="tds", icon="mdi:water", unit_of_measurement="tds")], True)

class PetoneerSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator: DataUpdateCoordinator, hass, name=None, data_attribute=None, icon="mdi:water-percent", unit_of_measurement="%"):
        super().__init__(coordinator)
        self._state = None
        self._id = hass.data[DOMAIN]["conf"][CONF_SERIAL]
        self._name = name
        if name is None:
            self.entity_id = DOMAIN + "." + self._id
        else:
            self.entity_id = DOMAIN + "." + self._id + "_" + name.replace(" ", "_").lower()
        self._attr_device_info = coordinator.get_device()
        self._attr_icon = icon
        self.data_attribute = data_attribute
        self._attr_icon = icon
        self._unit_of_measurement = unit_of_measurement
        self._attrs = {}

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        if self._name is None:
            unique_id = self._id
        else:
            unique_id = self._id + "_" + self._name.replace(" ", "_").lower()
        return unique_id

    @property
    def device_info(self):
        return self._attr_device_info

    @property
    def name(self):
        if self._name is None:
            return f"Petoneer {self._id}"
        else:
            return f"Petoneer {self._id} {self._name}"

    @property
    def extra_state_attributes(self):
        return self._attrs

    @property
    def state(self):

        attributes = self.coordinator.data
        _LOGGER.debug(f"Sensor state: {attributes}")

        if not attributes:
            self._state = "unknown"
        else:
            self._attrs = {
                ATTR_LEVEL: attributes['level'],
                ATTR_TDS: attributes['tds'],
                ATTR_LED: attributes['led'],
                ATTR_LEDMODE: attributes['ledmode'],
                ATTR_FILTERTIME: attributes[ATTR_FILTERTIME],
                ATTR_MOTORTIME: attributes[ATTR_MOTORTIME],
                ATTR_WATERTIME: attributes[ATTR_WATERTIME],
                ATTR_ALARM: attributes['ledmode'] == 0,
                ATTR_SWITCH: attributes['switch']
            }
            if self.data_attribute is None:
                self._state = attributes['level'] * 25
            else:
                _LOGGER.debug(f"Using attribute: {self.data_attribute}")
                self._state = attributes[self.data_attribute]
        return self._state
