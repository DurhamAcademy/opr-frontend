import hid
import RPi.GPIO as GPIO
import config


class Nes(object):

    def __init__(self):
        try:
            for device in hid.enumerate():
                print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")
            self.nes_device = hid.device()
            self.nes_device.open(0x0079, 0x0126)
        except AttributeError:
            print("Unable to open device")

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(config.gps_mode_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        except:
            print("Unable to setup GPIO on NES/GPS Switch")

    def get_mode(self):
        """
        Check GPS mode or Controller Mode based on physical switch.
        """
        mode = GPIO.input(config.gps_mode_switch_pin)
        if mode == 1:
            return "gps"
        else:
            return "controller"

    def snes_input(self):
        report = self.nes_device.read(64)
        if report:
            if report[4] == 0 and report[9] == 255:
                self.gps_mode = False
                return ("up")
            elif report[4] == 255 and report[10] == 255:
                self.gps_mode = False
                return ("down")
            elif report[3] == 0 and report[8] == 255:
                self.gps_mode = False
                return ("left")
            elif report[3] == 255 and report[7] == 255:
                self.gps_mode = False
                return ("right")
            elif report[1] == 1:
                return ("select")
            elif report[1] == 2:
                return ("start")
            else:
                return ("neutral")

    def wpm_controller(self, control_input):
        try:
            if control_input == "neutral":
                left_speed = 0
                right_speed = 0
            elif control_input == "up":
                left_speed = -config.drive_speed
                right_speed = -config.drive_speed
            elif control_input == "down":
                left_speed = config.drive_speed
                right_speed = config.drive_speed
            elif control_input == "left":
                left_speed = config.drive_speed_turning
                right_speed = -config.drive_speed_turning
            elif control_input == "right":
                left_speed = -config.drive_speed_turning
                right_speed = config.drive_speed_turning
            else:
                left_speed = 0
                right_speed = 0
            return left_speed, right_speed
        except:
            left_speed, right_speed = 0, 0
            return left_speed, right_speed
