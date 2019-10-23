import board
import busio
import time
# Import NeoPixel Library
import neopixel
from digitalio import DigitalInOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager
import adafruit_requests as requests
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20
from mcgrail_webhooks import IO_HTTP, AdafruitIO_RequestError


try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Initialize one-wire bus on board pin D5.
ow_bus = OneWireBus(board.A3)

# Scan for sensors and grab the first one found.
ds181 = DS18X20(ow_bus, ow_bus.scan()[0])
ds182 = DS18X20(ow_bus,ow_bus.scan()[1])

print("ESP32 SPI webclient test")

TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
JSON_POST_URL = "https://webhooks.datazar.com/w0473c46f-88e9-42f7-8a30-f9fe85d54a08"

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

for ap in esp.scan_networks():
    print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(b'Mansion', b'gosnakes')
    except RuntimeError as e:
        print("could not connect to AP, retrying: ",e)
        continue
print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)
print("My IP address is", esp.pretty_ip(esp.ip_address))
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
aio_username = secrets['aio_username']
aio_key = secrets['aio_key']

# Create an instance of the Adafruit IO HTTP client
io = IO_HTTP(JSON_POST_URL, wifi)

ntp = NTP(esp)

# Fetch and set the microcontroller's current UTC time
# keep retrying until valid time is returned
while True:
    try:
        ntp.set_time()
        break
    except ValueError as e:
        print("error gettiing time - retrying in 5 seconds: ", e)
        time.sleep(5)
        continue

while True:
    try:
        temperature1 = '{0:0.3f}'.format(ds181.temperature)
        temperature2 = '{0:0.3f}'.format(ds182.temperature)
        print('Current Temperature: {0}*C'.format(temperature1))
        print('Current Temperature: {0}*C'.format(temperature2))
        current_time = time.time()
        # Convert the current time in seconds since Jan 1, 1970 to a struct_time
        now = time.localtime(current_time)
        print(now)
        # Pretty-parse the struct_time
        ctime = '{}/{}/{} at {}:{}:{} UTC'.format(
            now.tm_mon, now.tm_mday, now.tm_year,
            now.tm_hour,now.tm_min, now.tm_sec))
        data = {
                "TimeStamp":ctime,
                "DeviceIDs":["1","2"],
                "Temperatures":[temperature1,temperature2]
                }
        print('Sending to...')
        print(data)
        io.send_data(JSON_POST_URL, data)
        print('Data sent!')
    except (ValueError, RuntimeError) as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue
    time.sleep(10)


#while True:
#    print('Temperature: {0:0.3f}C'.format(ds18.temperature))
#    temp = '{0:0.3f}C'.format(ds18.temperature)
#    json_data = {"Temperature" : temp}
#   print("POSTing data to {0}: {1}".format(JSON_POST_URL, json_data))
#    requests.post(JSON_POST_URL, json=json_data)
#    print('-'*40)
#    time.sleep(10.0)