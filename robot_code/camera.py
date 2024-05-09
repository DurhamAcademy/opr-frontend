import RPi.GPIO as GPIO
import config
import time


# Sets the pin numbering system to use the physical layout
GPIO.setmode(GPIO.BCM)
GPIO.setup(config.camera_io_alarm_pin, GPIO.OUT)


def enable_camera():
    GPIO.output(config.camera_io_alarm_pin, GPIO.HIGH)


def disable_camera():
    GPIO.output(config.camera_io_alarm_pin, GPIO.LOW)

