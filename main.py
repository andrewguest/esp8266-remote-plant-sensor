import sys
import machine
import time
import urequests
import json

from umqtt.simple import MQTTClient

import config


def deepsleep(sleep_duration_seconds):
    # Deep sleep setup
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    # set RTC.ALARM0 to fire after <sleep_duration_seconds> seconds (waking the device)
    rtc.alarm(rtc.ALARM0, sleep_duration_seconds * 1000)

    # put the device to sleep
    machine.deepsleep()


def getDateTime():
    response = urequests.get("https://worldtimeapi.org/api/timezone/America/Chicago")
    current_datetime = response.json()["datetime"]
    current_datetime = current_datetime.split(".")[0]
    current_datetime = current_datetime.replace("T", " ")
    return current_datetime


def getBatteryPercentage():
    # Get an analog reading from 0 to 1024
    # 0 being 0v and 1024 being 3.3v (since this pin can handle 3.3v input)
    analog_pin = machine.ADC(0)

    # Read the analog pin
    analog_reading = analog_pin.read()

    # Convert the input into a voltage on a scale of 0v to 4.2v for this type of battery
    voltage = analog_reading * 0.00486

    # Divde the voltage by 0.05 because instead of 0v being "dead", batteries are "dead"
    #   when they drop below 3.2v, so we only have 1v between "full" (4.2v) and "dead" (3.2v)
    #      1v / 100% = 0.05v so each 0.05v is 1% of the battery's charge
    # 0%   = 3.2v
    # 50%  = 3.7v
    # 100% = 4.2v
    percentage = voltage / 0.05

    # Reduce the output to 2 decimal places so it's nicer to read
    percentage = float("{:.2f}".format(percentage))
    return percentage


# MQTT client setup
mqtt_client = MQTTClient(
    "plant-esp8266",
    "io.adafruit.com",
    port=8883,
    user=config.adafruit_io_username,
    password=config.adafruit_io_key,
    ssl=True,
)

connect_status = mqtt_client.connect()
mqtt_client.sock.setblocking(False)


def mqtt_publish():
    if connect_status != 0:
        print("Error connecting to the MQTT broker")
        sys.exit(1)

    dt = getDateTime()
    bat_percent = getBatteryPercentage()
    bat_percent = str(bat_percent)

    # publish the "bat_percent" data to the "wemos-d1-testing.battery" topic
    mqtt_client.publish(
        config.adafruit_io_username + "/feeds/wemos-d1-testing.battery", bat_percent
    )

    mqtt_client.publish(
        config.adafruit_io_username + "/feeds/wemos-d1-testing.datetime", dt
    )

    # Add a delay to allow MQTT to send the data to the broker
    time.sleep(2)

    # send the esp8266 to sleep for 60 seconds
    deepsleep(60)


mqtt_publish()
