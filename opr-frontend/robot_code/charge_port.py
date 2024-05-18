import RPi.GPIO as GPIO
import config

GPIO.setmode(GPIO.BCM)
GPIO.setup(config.charge_plug_sensor, GPIO.IN)


def charge_port_status():
    if GPIO.input(config.charge_plug_sensor) == 0:
        return True
    else:
        return False
