import RPi.GPIO as GPIO

drive_speed = 80
drive_speed_turning = 30
motor_left_direction_pin = 17
motor_right_direction_pin = 27
motor_left_speed_pin = 13
motor_right_speed_pin = 12

GPIO.setmode(GPIO.BCM)

GPIO.setup(motor_left_direction_pin, GPIO.OUT)
GPIO.setup(motor_right_direction_pin, GPIO.OUT)

GPIO.setup(motor_left_speed_pin, GPIO.OUT)
GPIO.setup(motor_right_speed_pin, GPIO.OUT)

right_motor = GPIO.PWM(motor_right_speed_pin, 50)
right_motor.start(0)
left_motor = GPIO.PWM(motor_left_speed_pin, 50)
left_motor.start(0)

GPIO.output(motor_left_direction_pin, GPIO.HIGH)
GPIO.output(motor_right_direction_pin, GPIO.HIGH)


def set_right_speed(speed: int):
    if speed >= 0:
        GPIO.output(motor_right_direction_pin, GPIO.HIGH)
    else:
        GPIO.output(motor_right_direction_pin, GPIO.LOW)
    right_motor.ChangeDutyCycle(abs(speed))


def set_left_speed(speed: int):
    if speed >= 0:
        GPIO.output(motor_left_direction_pin, GPIO.HIGH)
    else:
        GPIO.output(motor_left_direction_pin, GPIO.LOW)
    left_motor.ChangeDutyCycle(abs(speed))
