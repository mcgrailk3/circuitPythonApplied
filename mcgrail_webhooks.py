# The MIT License (MIT)
#
# Copyright (c) 2019 Kevin McGrail
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`mcgrail_mcgrail_webhooks`
================================================================================

CircuitPython helper library for webhooks hooks


* Author(s): Kevin McGrail

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s). Use unordered list & hyperlink rST
   inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

import time
import json
from mcgrail_hooks_errors import (
    AdafruitIO_RequestError,
    AdafruitIO_ThrottleError,
)

__version__ = "0.0.0-auto.0"

CLIENT_HEADERS = {"User-Agent": "AIO-CircuitPython/{0}".format(__version__)}

class IO_HTTP:
    """
    Client for interacting with the Adafruit IO HTTP API.
    https://io.adafruit.com/api/docs/#adafruit-io-http-api
        :param str url
        :param wifi_manager: WiFiManager object from ESPSPI_WiFiManager or ESPAT_WiFiManager
    """

    def __init__(self, url, wifi_manager):
        self.url = url
        wifi_type = str(type(wifi_manager))
        if "ESPSPI_WiFiManager" in wifi_type or "ESPAT_WiFiManager" in wifi_type:
            self.wifi = wifi_manager
        else:
            raise TypeError("This library requires a WiFiManager object.")
        self._aio_headers = [
            {"Content-Type": "application/json"},
        ]

    @staticmethod
    def _create_headers(io_headers):
        """Creates http request headers.
        """
        headers = CLIENT_HEADERS.copy()
        headers.update(io_headers)
        return headers

    @staticmethod
    def _create_data(data, metadata):
        """Creates JSON data payload
        """
        if metadata is not None:
            return {
                "value": data,
                "lat": metadata["lat"],
                "lon": metadata["lon"],
                "ele": metadata["ele"],
                "created_at": metadata["created_at"],
            }
        return data

    @staticmethod
    def _handle_error(response):
        """Checks HTTP status codes
        and raises errors.
        """
        if response.status_code == 429:
            raise AdafruitIO_ThrottleError
        elif response.status_code == 400:
            raise AdafruitIO_RequestError(response)
        elif response.status_code >= 400:
            raise AdafruitIO_RequestError(response)

    def _compose_path(self, path):
        """Composes a valid API request path.
        :param str path: Adafruit IO API URL path.
        """
        print(path)
        return path

    # HTTP Requests
    def _post(self, path, payload):
        """
        POST data to Adafruit IO
        :param str path: Formatted Adafruit IO URL from _compose_path
        :param json payload: JSON data to send to Adafruit IO
        """
        response = self.wifi.post(
            path, json=payload, headers=self._create_headers(self._aio_headers[0])
        )
        self._handle_error(response)
        return response.json()

    def _get(self, path):
        """
        GET data from Adafruit IO
        :param str path: Formatted Adafruit IO URL from _compose_path
        """
        response = self.wifi.get(
            path, headers=self._create_headers(self._aio_headers[1])
        )
        self._handle_error(response)
        return response.json()

    def _delete(self, path):
        """
        DELETE data from Adafruit IO.
        :param str path: Formatted Adafruit IO URL from _compose_path
        """
        response = self.wifi.delete(
            path, headers=self._create_headers(self._aio_headers[0])
        )
        self._handle_error(response)
        return response.json()

    # Data
    def send_data(self, url, data, metadata=None, precision=None):
        """
        Sends value data to a specified Adafruit IO feed.
        :param str feed_key: Adafruit IO feed key
        :param str data: Data to send to the Adafruit IO feed
        :param dict metadata: Optional metadata associated with the data
        :param int precision: Optional amount of precision points to send with floating point data
        """
        path = self._compose_path(url)
        if precision:
            try:
                data = round(data, precision)
            except NotImplementedError:  # received a non-float value
                raise NotImplementedError("Precision requires a floating point value")
        payload = self._create_data(data, metadata)
        self._post(path, payload)

    def receive_data(self, feed_key):
        """
        Return the most recent value for the specified feed.
        :param string feed_key: Adafruit IO feed key
        """
        path = self._compose_path("feeds/{0}/data/last".format(feed_key))
        return self._get(path)
