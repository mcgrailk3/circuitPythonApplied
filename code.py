import board
import busio
import time
from adafruit_ntp import NTP
# Import NeoPixel Library
import neopixel
from digitalio import DigitalInOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
import adafruit_requests as requests
from adafruit_onewire.bus import OneWireBus, OneWireAddress

from mcgrail_webhooks import IO_HTTP, AdafruitIO_RequestError
from adafruit_ds18x20 import DS18X20
from mcgrail_hooks_errors import (
    AdafruitIO_RequestError,
    AdafruitIO_ThrottleError,
)

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

try:
    from data import data
except ImportError:
    print("Metadata is kept in Data.py, please add it there!")
    raise

location = data['location']
latitude = data['latitude']
longitude = data['longitude']
# Initialize one-wire bus on board pin D5.
ow_bus = OneWireBus(board.A3)
oneWire = ow_bus.scan()

# Scan for sensors and grab the first one found.
sensors =[]

#Fill sensors array with oneWire objects
for i, d in enumerate(oneWire):
    serial = ""
    for byte in d.serial_number:
        #print("{:02x}".format(byte), end='')
        serial = serial + "{:02x}".format(byte)
    sensor = {"Serial Number" : serial, "ow" : DS18X20(ow_bus, ow_bus.scan()[i])}
    sensors.append(sensor)
    t = '{0:0.3f}'.format(DS18X20(ow_bus, ow_bus.scan()[i]).temperature)
    ds18 = DS18X20(ow_bus, ow_bus.scan()[i])
    ds18.resolution = 12

JSON_POST_URL = "https://udsensors.tk/api/Feather/"

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.D13)
esp32_ready = DigitalInOut(board.D11)
esp32_reset = DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")

while not esp.is_connected:
    try:
        esp.connect(secrets)
    except RuntimeError as e:
        print("could not connect to AP, retrying: ",e)
        continue
print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
key = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoic2xpZGluZyIsImV4cCI6MTYxMTk1NjA5MSwianRpIjoiYThhNThhNDAzODBhNGU3NzlkMjFhYTExMzE3YjE5NmMiLCJyZWZyZXNoX2V4cCI6MTY0MzQ5MjA5MSwidXNlcl9pZCI6M30.xAZq-CqJNzBADDklkd7wOOwEX3khX5_gKkBx0h1ZouI"
key = data['key']
#io = IO_HTTP(JSON_POST_URL, key, wifi)
ntp = NTP(esp)

# Fetch and set the microcontroller's current UTC time
# keep retrying until valid time is returned
while not ntp.valid_time:
    ntp.set_time()
    print("Failed to obtain time, retrying in 5 seconds...")
    time.sleep(5)
current_time = time.time()

# Convert the current time in seconds since Jan 1, 1970 to a struct_time
now = time.localtime(current_time)
lat = 39.7771266
long = -83.9972517

while True:
    i = 0
    while i < 3:
        try:
            current_time = time.time()
            now = time.localtime(current_time)
            date = '{}-{}-{}'.format(now.tm_year, now.tm_mon, now.tm_mday)
            ctime = 'T{}:{}:{}'.format(now.tm_hour,now.tm_min, now.tm_sec)
            unixtime = date + ctime
            sensorData = []
            #Populate sensor data array
            for s in sensors:
                sensorData.append({"sensor_id": s["Serial Number"],
                                    "sensor_type": "Temperature",
                                    "sensor_data": s["ow"].temperature,
                                    "sensor_units": "C"
                                    })
            print(sensorData)
            data = {
                    "dev_id": 1,
                    "metadata": {
                          "location": "Apartment",
                          "latitude": 39.7771266,
                          "longitude": -83.9972517,
                          "time": unixtime
                    },
                    "data": sensorData
            }
            print(data)
            headers = {"Authorization" : key}
            response = wifi.post(JSON_POST_URL, json=data, headers=headers)
            #response = requests.post(JSON_POST_URL, json=data, headers=headers)
            #io.send_data(JSON_POST_URL, data)
            print('-'*40)
            json_resp = response.json()
            # Parse out the 'data' key from json_resp dict.
            print("Data received from server:", json_resp['data'])
            print('-'*40)
            response.close()
            print('Data sent!')
        except (ValueError, RuntimeError) as e:
            print('-'*40)
            print("Failed to get data, retrying\n", e)
            wifi.reset()
            continue
        #print(i)
        i+=1
        time.sleep(5)
    print('Sleeping for an hour')
    time.sleep(3600)