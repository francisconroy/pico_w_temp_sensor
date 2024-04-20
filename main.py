"""
A simple example that connects to the Adafruit IO MQTT server
and publishes values that represent a sine wave
"""
import socket
import time

import machine
import network

import ahtx0
from config import wifi_pass


class OnboardLED:
    def __init__(self):
        self.led = machine.Pin("LED", machine.Pin.OUT)
        self.blink_timer = machine.Timer()
        self.blink_counter = None

    def on(self):
        self.led.on()

    def off(self):
        self.led.off()

    def toggle(self):
        self.led.toggle()

    def blink_toggle(self, timer):
        self.toggle()
        if self.blink_counter is not None:
            self.blink_counter -= 1
            if self.blink_counter <= 0:
                self.blink_stop()
                self.blink_counter = None

    def blink_count(self, count):
        self.blink_counter = count
        self.blink_start()

    def blink_start(self, freq):
        self.blink_timer.init(freq=freq, mode=machine.Timer.PERIODIC,
                              callback=self.blink_toggle)

    def blink_stop(self):
        self.blink_timer.deinit()


def connect_wifi():
    # Fill in your WiFi network name (ssid) and password here:
    wifi_ssid = "fiyevgee"
    wifi_password = wifi_pass

    # Connect to WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    print("Connected to WiFi")
    print(wlan.ifconfig())


def run_webserver(sensor_instance=None):
    html = """<!DOCTYPE html>
    <html>
        <head> <title>Pico W</title> </head>
        <body> <h1>Pico W</h1>
            <table>
            <tr><td>Temperature:</td><td>{temp}</td></tr>
            <tr><td>Humidity:</td><td>{humidity}</td></tr>
        </body>
    </html>
    """

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('listening on', addr)

    # Listen for connections
    while True:
        try:
            cl, addr = s.accept()
            print('client connected from', addr)
            request = cl.recv(1024)
            print(request)

            request = str(request)

            # Get latest temperature and humidity from AHT-20 sensor

            response = html.format(temp=sensor_instance.temperature, humidity=sensor_instance.relative_humidity)

            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(response)
            cl.close()

        except OSError as e:
            cl.close()
            print('connection closed')


led = OnboardLED()
led.blink_start(2)
connect_wifi()
led.blink_stop()
led.on()
mid = machine.unique_id()
for i in mid:
    print(hex(i))

i2c = machine.I2C(0, freq=50000)  # create I2C peripheral at frequency of 400kHz
# depending on the port, extra parameters may be required
# to select the peripheral and/or pins to use

for item in i2c.scan():  # scan for peripherals, returning a list of 7-bit addresses
    print(item)

# Create the sensor object using I2C
sensor = ahtx0.AHT10(i2c)
run_webserver(sensor)

# i2c.writeto(42, b'123')         # write 3 bytes to peripheral with 7-bit address 42
# i2c.readfrom(42, 4)             # read 4 bytes from peripheral with 7-bit address 42
#
# i2c.readfrom_mem(42, 8, 3)      # read 3 bytes from memory of peripheral 42,
#                                 #   starting at memory-address 8 in the peripheral
# i2c.writeto_mem(42, 2, b'\x10') # write 1 byte to memory of peripheral 42
#                                 #   starting at address 2 in the peripheral
