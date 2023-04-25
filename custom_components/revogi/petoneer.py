"""
Python module to get device details from Petoneer / Revogi equipment
Tested with a Petoneer Fresco Pro water fountain
"""

import asyncio
import hashlib
import json
import logging
import urllib.parse

import aiohttp
from opcode import hasconst

REQUIREMENTS = ["aiohttp"]

_LOGGER = logging.getLogger(__name__)

class Petoneer:
    """
    Class to interface with the cloud-based API for the Revogi Smart Home equipment
    """

    API_URL                 = "https://as.revogi.net/app"

    API_LOGIN_PATH          = "/user/101"
    API_DEVICE_LIST_PATH    = "/user/500"
    API_DEVICE_DETAILS_PATH = "/pww/31101"
    API_DEVICE_SWITCH_PATH  = "/pww/21101"
    Debug                   = 0
    hass             = False

    def __init__(self):
        # Nothing to do here
        _LOGGER.debug("Petoneer Python API")


    async def _debug(self, msg):
        _LOGGER.debug(msg)

    def _url(self, path):
        return self.API_URL + path

    async def _req(self, path, payload, auth=True):
        if (auth):
            headers = { "accessToken": self._auth_token }
        else:
            headers = {}

        async with aiohttp.ClientSession() as session:
            async with await session.post(self._url(path), json=payload, headers=headers) as resp:
                response = await resp.json()

        await session.close()
        return response

    async def auth(self, username, password):
        # Build the authentication request payload
        auth_payload = {
          "language": "0",
          "type": 2,
          "region": {
            "country": "AU",
            "timezone": "Australia/Sydney"
          },
          "username": username,
          "password": password
        }

        _LOGGER.debug("Authenticating to " + str(self.API_URL) + " as " + username + "...")

        #
        # Attempt to authenticate - if successful, we will get an HTTP 200
        # response back which will include our authentication token that
        # we need to use for subsequent requests.
        #
        resp = await self._req(self.API_LOGIN_PATH, auth_payload, auth=False)
        _LOGGER.debug(resp)
        json_resp = resp

        # Verify we have an auth token in the response - if so, store it
        if (json_resp['data']['accessToken']):
            self._auth_token = json_resp['data']['accessToken']
            _LOGGER.debug("Authentication successful - token ***" + self._auth_token[-4:])
        else:
            raise RuntimeError("No token value in response payload")


    async def get_registered_devices(self):
        _LOGGER.info("Getting All Devices")
        payload = {
          "dev": "all",
          "protocol": "3"
        }
        resp = await  self._req(self.API_DEVICE_LIST_PATH, payload)
        json_resp = resp

        devices =  json_resp['data']['dev']

        # Return the list of devices
        return devices

    async def fetch_data(self, device_code):
        return await self.get_device_details(device_code)

    async def get_device_details(self, device_code):
        _LOGGER.info("Getting details for device " + device_code)
        payload = { "sn": device_code, "protocol": "3" }
        resp = await self._req(self.API_DEVICE_DETAILS_PATH, payload)
        json_resp = resp

        _LOGGER.debug(f"Device Response: {json_resp}")
        if "data" in json_resp:
            device_details = json_resp['data']
            _LOGGER.debug(f"Returning {device_details}")
        else:
            device_details = False
        return device_details

    async def turn_on(self, device_code):
        payload = { "sn": device_code, "protocol": "3", "switch": 1 }
        resp = await self._req(self.API_DEVICE_SWITCH_PATH, payload)
        json_resp = resp

        device_details = json_resp['data']
        return device_details

    async def turn_off(self, device_code):
        payload = { "sn": device_code, "protocol": "3", "switch": 0 }
        resp = await self._req(self.API_DEVICE_SWITCH_PATH, payload)
        json_resp = resp

        device_details = json_resp['data']
        return device_details
