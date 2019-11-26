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

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Initialize one-wire bus on board pin D5.
ow_bus = OneWireBus(board.A3)
data1 = ow_bus.scan()[1].rom
print(data1)

print(ow_bus.scan()[0].rom)
print(OneWireAddress(ow_bus.scan()[0]).rom)
# Scan for sensors and grab the first one found.
ds181 = DS18X20(ow_bus, ow_bus.scan()[0])
ds182 = DS18X20(ow_bus, ow_bus.scan()[1])

print("ESP32 SPI webclient test")

TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_POST_URL = "https://webhooks.datazar.com/webd77c9b-d6b9-4047-98ac-8701ab1dcd73"
JSON_POST_URL2 = "https://udsensors.tk/ws/api/Feather/"

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
        esp.connect_AP(b'Mansion', b'gosnakes')
    except RuntimeError as e:
        print("could not connect to AP, retrying: ",e)
        continue
print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

# Create an instance of the Adafruit IO HTTP client
io = IO_HTTP(JSON_POST_URL, wifi)
io2 = IO_HTTP(JSON_POST_URL2, wifi)
ntp = NTP(esp)

# Fetch and set the microcontroller's current UTC time
# keep retrying until valid time is returned
while True:
    try:
        ntp.set_time()
        break
    except ValueError as e:
        print("error getting time - retrying in 5 seconds: ", e)
        time.sleep(5)
        continue
lat = 39.7771266
long = -83.9972517

while True:
    i = 0
    while i < 3:
        try:
            temperature1 = '{0:0.3f}'.format(ds181.temperature)
            temperature2 = '{0:0.3f}'.format(ds182.temperature)
            print('Current Temperature: {0}*C'.format(temperature1))
            print('Current Temperature: {0}*C'.format(temperature2))
            current_time = time.time()
            # Convert the current time in seconds since Jan 1, 1970 to a struct_time
            now = time.localtime(current_time)
            # Pretty-parse the struct_time
            date = '{}-{}-{}'.format(now.tm_year, now.tm_mon, now.tm_mday)
            ctime = 'T{}:{}:{}'.format(now.tm_hour,now.tm_min, now.tm_sec)
            unixtime = date + ctime
            data = {
                    "dev_id": 1,
                    "metadata": {
                          "location": "Apartment",
                          "latitude": 39.7771266,
                          "longitude": -83.9972517,
                          "time": unixtime
                    },
                    "data": [
                        {
                         "sensor_id": 1,
                         "sensor_type": "Temperature",
                         "sensor_data": temperature1,
                         "sensor_units": "C"
                        },
                        {
                         "sensor_id": 2,
                         "sensor_type": "Temperature",
                         "sensor_data": temperature2,
                         "sensor_units": "C"
                        }
                    ]
            }
            print('Sending to...')
            print(data)
            #io.send_data(JSON_POST_URL, data)
            io2.send_data(JSON_POST_URL2, data)
            print('Data sent!')
        except (ValueError, RuntimeError) as e:
            print("Failed to get data, retrying\n", e)
            wifi.reset()
            continue
        print(i)
        i+=1
        time.sleep(5)
    print('Sleeping for an hour')
    time.sleep(3600)