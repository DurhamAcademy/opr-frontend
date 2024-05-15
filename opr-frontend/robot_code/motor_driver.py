import RPi.GPIO as GPIO
import config
import time


"""
Using a class for motor control
Uses an init method to initialize motors once
"""


class Motor(object):
    def __init__(self):
        # Sets the pin numbering system to use the physical layout
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(config.motor_left_direction_pin, GPIO.OUT)
        GPIO.setup(config.motor_right_direction_pin, GPIO.OUT)
        GPIO.setup(config.safety_light_pin, GPIO.OUT)
        GPIO.setup(config.motor_left_speed_pin, GPIO.OUT)
        GPIO.setup(config.motor_right_speed_pin, GPIO.OUT)

        self.right_motor = GPIO.PWM(config.motor_right_speed_pin, 50)
        self.right_motor.start(0)
        self.left_motor = GPIO.PWM(config.motor_left_speed_pin, 50)
        self.left_motor.start(0)

        GPIO.output(config.motor_left_direction_pin, GPIO.HIGH)
        GPIO.output(config.motor_right_direction_pin, GPIO.HIGH)

        self.last_motor_command = 0.00

        # Turn on Safety light
        GPIO.output(config.safety_light_pin, GPIO.HIGH)

    def safety_light_timeout(self):
        if self.last_motor_command + config.safety_light_timeout < time.time():
            # if pin is high, go low
            if GPIO.input(config.safety_light_pin):
                GPIO.output(config.safety_light_pin, GPIO.LOW)
        else:
            GPIO.output(config.safety_light_pin, GPIO.HIGH)

    def set_right_speed(self, speed: int):
        """
        :param speed: Speed of right motor, negative for backwards (range unknown) TODO: Find out range
        :return: null
        """

        self.last_motor_command = time.time()
        self.safety_light_timeout()

        if speed >= 0:
            GPIO.output(config.motor_right_direction_pin, GPIO.HIGH)
        else:
            GPIO.output(config.motor_right_direction_pin, GPIO.LOW)
        self.right_motor.ChangeDutyCycle(abs(speed))

    def set_left_speed(self, speed: int):
        """
        :param speed: Speed of left motor, negative for backwards (range unknown) TODO: Find out range
        :return: null
        """

        self.last_motor_command = time.time()
        self.safety_light_timeout()

        if speed >= 0:
            GPIO.output(config.motor_left_direction_pin, GPIO.HIGH)
        else:
            GPIO.output(config.motor_left_direction_pin, GPIO.LOW)
        self.left_motor.ChangeDutyCycle(abs(speed))

    def drive_stop(self):
        self.set_left_speed(0)
        self.set_right_speed(0)
        return

    def drive_forward(self):
        self.last_motor_command = time.time()
        self.set_left_speed(-80)
        self.set_right_speed(-80)
        return

    def drive_turn_right(self, speed):
        self.last_motor_command = time.time()
        # self.set_left_speed(0)
        self.set_right_speed(-1 * speed)
        self.set_left_speed(speed)
        return

    def drive_turn_left(self, speed):
        self.last_motor_command = time.time()
        self.set_right_speed(speed)
        # self.set_right_speed(0)
        self.set_left_speed(-1 * speed)
        return

    def drive_reverse(self):
        self.last_motor_command = time.time()
        self.set_left_speed(30)
        self.set_right_speed(30)
        return

    def cleanup(self):
        # Clean up everything
        self.right_motor.stop()
        self.left_motor.stop()
        GPIO.output(config.safety_light_pin, GPIO.LOW)
