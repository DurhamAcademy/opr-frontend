import nes
import motor_driver

controller = nes.Nes()
drive = motor_driver.Motor()

while True:
    left_speed, right_speed = controller.wpm_controller(controller.snes_input())
    drive.set_left_speed(left_speed)
    drive.set_right_speed(right_speed)