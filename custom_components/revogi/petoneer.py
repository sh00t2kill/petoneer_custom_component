"""
Python module to get device details from Petoneer / Revogi equipment
Tested with a Petoneer Fresco Pro water fountain
"""

import logging
import urllib.parse

import requests
import json
import hashlib
from pprint import pprint

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

    def __init__(self):
        # Nothing to do here
        if (self.Debug):
            print("Petoneer Python API via the Dark Arts")
            print("====================================")
            print("")

    
    def _debug(self, msg):
        #print(msg)
        pass

    def _url(self, path):
        return self.API_URL + path

    def _req(self, path, payload, auth=True):
        if (auth):
            headers = { "accessToken": self._auth_token }
        else:
            headers = {}

        # Make the request
        resp = requests.post(self._url(path), json=payload, headers=headers)
        return resp

    def auth(self, username, password):
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
        
        if (self.Debug):
            print("Authenticating to " + self.API_URL + " as " + username + "...")

        #
        # Attempt to authenticate - if successful, we will get an HTTP 200
        # response back which will include our authentication token that
        # we need to use for subsequent requests.
        #
        resp = self._req(self.API_LOGIN_PATH, auth_payload, auth=False)
        json_resp = resp.json()

        # Verify we have an auth token in the response - if so, store it
        if (json_resp['data']['accessToken']):
            self._auth_token = json_resp['data']['accessToken']
            if (self.Debug):
                print("Authentication successful - token ***" + self._auth_token[-4:])
        else:
            raise RuntimeError("No token value in response payload")


    def get_registered_devices(self):
        if (self.Debug):
            print("Getting All Devices")
        payload = {
          "dev": "all",
          "protocol": "3"
        }
        resp = self._req(self.API_DEVICE_LIST_PATH, payload)
        json_resp = resp.json()

        devices =  json_resp['data']['dev']

        # Return the list of devices
        return devices

    def get_device_details(self, device_code):
        if (self.Debug):
            print("Getting details for device " + device_code)
        payload = { "sn": device_code, "protocol": "3" }
        resp = self._req(self.API_DEVICE_DETAILS_PATH, payload)
        json_resp = resp.json()
  
        device_details = json_resp['data']
        return device_details

    def turn_on(self, device_code):
        payload = { "sn": device_code, "protocol": "3", "switch": 1 }
        resp = self._req(self.API_DEVICE_SWITCH_PATH, payload)
        json_resp = resp.json()

        device_details = json_resp['data']
        return device_details

    def turn_off(self, device_code):
        payload = { "sn": device_code, "protocol": "3", "switch": 0 }
        resp = self._req(self.API_DEVICE_SWITCH_PATH, payload)
        json_resp = resp.json()

        device_details = json_resp['data']
        return device_details

