import RPi.GPIO as GPIO

drive_speed = 80
drive_speed_turning = 30
motor_left_direction_pin = 17
motor_right_direction_pin = 27
motor_left_speed_pin = 13
motor_right_speed_pin = 12


def controller(control_input):
    try:
        if control_input == "neutral":
            left_speed = 0
            right_speed = 0
        elif control_input == "up":
            left_speed = -drive_speed
            right_speed = -drive_speed
        elif control_input == "down":
            left_speed = drive_speed
            right_speed = drive_speed
        elif control_input == "left":
            left_speed = drive_speed_turning
            right_speed = -drive_speed_turning
        elif control_input == "right":
            left_speed = -drive_speed_turning
            right_speed = drive_speed_turning
        else:
            left_speed = 0
            right_speed = 0
        return left_speed, right_speed
    except:
        left_speed, right_speed = 0, 0
        return left_speed, right_speed


def set_right_speed(speed: int):
    if speed >= 0:
        GPIO.output(motor_right_direction_pin, GPIO.HIGH)
    else:
        GPIO.output(motor_right_direction_pin, GPIO.LOW)
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