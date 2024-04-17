"""
A simple example that connects to the Adafruit IO MQTT server
and publishes values that represent a sine wave
"""

import time
from math import sin

import network
import machine
from umqtt.simple import MQTTClient


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
        self.blink_timer.init(freq=freq, mode=machine.Timer.PERIODIC, callback=self.blink_toggle)

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

led = OnboardLED()
led.blink_start(2)
connect_wifi()
led.blink_stop()
led.on()



# Fill in your Adafruit IO Authentication and Feed MQTT Topic details
mqtt_host = "io.adafruit.com"
mqtt_username = ""  # Your Adafruit IO username
mqtt_password = ""  # Adafruit IO Key
mqtt_publish_topic = ""  # The MQTT topic for your Adafruit IO Feed

# Enter a random ID for this MQTT Client
# It needs to be globally unique across all of Adafruit IO.
mqtt_client_id = "somethingreallyrandomandunique123"

# Initialize our MQTTClient and connect to the MQTT server
mqtt_client = MQTTClient(
    client_id=mqtt_client_id,
    server=mqtt_host,
    user=mqtt_username,
    password=mqtt_password)

mqtt_client.connect()

# Publish a data point to the Adafruit IO MQTT server every 3 seconds
# Note: Adafruit IO has rate limits in place, every 3 seconds is frequent
#  enough to see data in realtime without exceeding the rate limit.
counter = 0
try:
    while True:
        # Generate some dummy data that changes every loop
        sine = sin(counter)
        counter += .8

        # Publish the data to the topic!
        print(f'Publish {sine:.2f}')
        mqtt_client.publish(mqtt_publish_topic, str(sine))

        # Delay a bit to avoid hitting the rate limit
        time.sleep(3)
except Exception as e:
    print(f'Failed to publish message: {e}')
finally:
    mqtt_client.disconnect()
