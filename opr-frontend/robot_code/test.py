# Test file
import time
import RPi.GPIO as GPIO
import config

GPIO.setmode(GPIO.BCM)

while True:
    time.sleep(2)
    if GPIO.input(config.charge_plug_sensor) == 1:
        print("on")
    else:
        print("off")