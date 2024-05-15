import config
import RPi.GPIO as GPIO
import time
import os
import subprocess
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(config.gps_mode_switch_pin, GPIO.IN)

while True:
    if GPIO.input(config.gps_mode_switch_pin) == 1:
        # GPS Mode remains
        time.sleep(3)
        continue

    else:
        last_mode = GPIO.input(config.gps_mode_switch_pin)
        # Stop GPS
        os.system("sudo systemctl stop opr-frontend.service")
        # Start RC
        os.system("sudo python enable_rc.py")




