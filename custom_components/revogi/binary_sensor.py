import asyncio
from datetime import datetime, timedelta
import hashlib
import json
import logging
import urllib.parse

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import *
from homeassistant.helpers.update_coordinator import (CoordinatorEntity,
                                                      DataUpdateCoordinator)

from .const import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):
    """Setup the sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities([PetoneerSensor(coordinator, hass)], True)

class PetoneerSensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator: DataUpdateCoordinator, hass):
        super().__init__(coordinator)
        self._state = None
        self._id = hass.data[DOMAIN]["conf"][CONF_SERIAL]
        self.entity_id = DOMAIN + "." + self._id

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
        return f"Petoneer Consumables Alert {self._id}"

    @property
    def state(self):
        attributes = self.coordinator.data
        filtertime = attributes[ATTR_FILTERTIME]
        motortime =  attributes[ATTR_MOTORTIME]
        watertime =  attributes[ATTR_WATERTIME]
        _LOGGER.debug(f"Binary Sensor state: {attributes}")

        filterdue = self.is_due(FILTER_DURATION, filtertime)
        motordue = self.is_due(MOTOR_TIME, motortime)
        waterdue = self.is_due(WATER_DURATION, watertime)

        _LOGGER.debug(f"Filter due: {filterdue}")
        _LOGGER.debug(f"Motor due: {motordue}")
        _LOGGER.debug(f"Water due: {waterdue}")

        self._state = "off" if (filterdue or motordue or waterdue) else "off"
        return self._state

    def is_due(self, days, time):
        due = datetime.now() + timedelta(days)
        delta = due - datetime.fromtimestamp(time)
        return delta.days < 0
