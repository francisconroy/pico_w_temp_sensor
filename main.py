"""
A simple example that connects to the Adafruit IO MQTT server
and publishes values that represent a sine wave
"""
import socket
import time

import machine
import network


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
    wifi_password = "supersecretpublicknowledge"

    # Connect to WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_ssid, wifi_password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    print("Connected to WiFi")
    print(wlan.ifconfig())


def run_webserver():
    html = """<!DOCTYPE html>
    <html>
        <head> <title>Pico W</title> </head>
        <body> <h1>Pico W</h1>
            <p>%s</p>
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

            response = html

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
run_webserver()




