import RPi.GPIO as GPIO
import config
import time
import socket


"""
Using a class for motor control
Uses an init method to initialize motors once
"""

# Sets the pin numbering system to use the physical layout
GPIO.setmode(GPIO.BCM)

GPIO.setup(config.motor_left_direction_pin, GPIO.OUT)
GPIO.setup(config.motor_right_direction_pin, GPIO.OUT)
GPIO.setup(config.safety_light_pin, GPIO.OUT)
GPIO.setup(config.motor_left_speed_pin, GPIO.OUT)
GPIO.setup(config.motor_right_speed_pin, GPIO.OUT)

right_motor = GPIO.PWM(config.motor_right_speed_pin, 50)
right_motor.start(0)
left_motor = GPIO.PWM(config.motor_left_speed_pin, 50)
left_motor.start(0)

GPIO.output(config.motor_left_direction_pin, GPIO.HIGH)
GPIO.output(config.motor_right_direction_pin, GPIO.HIGH)

last_motor_command = 0.00

# Turn off Safety light
GPIO.output(config.safety_light_pin, GPIO.LOW)


def safety_light_timeout():
    if last_motor_command + config.safety_light_timeout < time.time():
        # if pin is high, go low
        if GPIO.input(config.safety_light_pin):
            GPIO.output(config.safety_light_pin, GPIO.LOW)
    else:
        GPIO.output(config.safety_light_pin, GPIO.HIGH)


def set_right_speed(speed: int):
    """
    :param speed: Speed of right motor, negative for backwards (range unknown)
    :return: null
    """

    last_motor_command = time.time()
    safety_light_timeout()

    if speed >= 0:
        GPIO.output(config.motor_right_direction_pin, GPIO.HIGH)
    else:
        GPIO.output(config.motor_right_direction_pin, GPIO.LOW)
    right_motor.ChangeDutyCycle(abs(speed))


def set_left_speed(speed: int):
    """
    :param speed: Speed of left motor, negative for backwards (range unknown)
    :return: null
    """

    last_motor_command = time.time()
    safety_light_timeout()

    if speed >= 0:
        GPIO.output(config.motor_left_direction_pin, GPIO.HIGH)
    else:
        GPIO.output(config.motor_left_direction_pin, GPIO.LOW)
    left_motor.ChangeDutyCycle(abs(speed))


def drive_stop():
    set_left_speed(0)
    set_right_speed(0)
    return


def drive_forward():
    last_motor_command = time.time()
    set_left_speed(-80)
    set_right_speed(-80)
    return


def drive_turn_right(speed):
    last_motor_command = time.time()
    # set_left_speed(0)
    set_right_speed(-1 * speed)
    set_left_speed(speed)
    return


def drive_turn_left(speed):
    last_motor_command = time.time()
    set_right_speed(speed)
    # set_right_speed(0)
    set_left_speed(-1 * speed)
    return


def drive_reverse():
    last_motor_command = time.time()
    set_left_speed(30)
    set_right_speed(30)
    return


def main():
    host = 'localhost'
    port = 55001
    buffer_size = 1024

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}")

        while True:
            client_socket, addr = server_socket.accept()
            with client_socket:
                print(f"Connected by {addr}")
                while True:
                    safety_light_timeout()
                    try:
                        data = client_socket.recv(buffer_size)
                        if not data:
                            break
                        command = data.decode('utf-8')
                        # print(f"Received command: {command}")
                        if command == 'stop':
                            drive_stop()
                        elif command == 'forward':
                            drive_forward()
                        elif command == 'reverse':
                            drive_reverse()
                        elif command == 'right':
                            drive_turn_right(config.drive_speed_turning)
                        elif command == 'left':
                            drive_turn_left(config.drive_speed_turning)

                        response = f"Command '{command}' received"
                        client_socket.sendall(response.encode('utf-8'))
                    except Exception as e:
                        print(e)


if __name__ == "__main__":
    main()
