import asyncio
import hashlib
import json
import logging
import urllib.parse
from datetime import datetime, timedelta

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
    async_add_entities([PetoneerBinarySensor(coordinator, hass, ATTR_FILTERTIME, FILTER_DURATION, "Filter")], True)
    async_add_entities([PetoneerBinarySensor(coordinator, hass, ATTR_WATERTIME, WATER_DURATION, "Water")], True)
    async_add_entities([PetoneerBinarySensor(coordinator, hass, ATTR_MOTORTIME, MOTOR_TIME, "Motor")], True)

class PetoneerBinarySensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator: DataUpdateCoordinator, hass, time, days, name):
        super().__init__(coordinator)
        self._state = None
        self._id = hass.data[DOMAIN]["conf"][CONF_SERIAL]
        self._time = time
        self._duration = days
        self._name = name

    def device_info(self):
        return {
            "name": f"{DEFAULT_NAME} {self._name}",
            "serial": self._id
        }

    @property
    def name(self):
        return f"Petoneer {self._name} Alert {self._id}"

    @property
    def state(self):
        attributes = self.coordinator.data
        _LOGGER.debug(f"Binary Sensor state: {attributes}")
        due = self.is_due(self._duration, attributes[self._time])
        self._state = "on" if due  else "off"
        return self._state

    def is_due(self, days, time):
        due = datetime.now() + timedelta(days)
        delta = due - datetime.fromtimestamp(time)
        return delta.days < 0
