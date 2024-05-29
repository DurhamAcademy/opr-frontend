import nes
import motor_driver

controller = nes.Nes()
drive = motor_driver.Motor()

try:
    previous_input = "neutral"
    while True:
        button_input = controller.snes_input()
        #print("button input : " + button_input)
        left_speed, right_speed = controller.wpm_controller(button_input)
        drive.set_left_speed(0)
        drive.set_right_speed(0)

        ramped_left_speed, ramped_right_speed = 0, 0

        # There has to be a better way to implement ramping.
        # This is a quick and dirty way.
        while button_input != previous_input:
            if left_speed > 0:
                if ramped_left_speed <= left_speed:
                    ramped_left_speed += 1
            else:
                if ramped_left_speed >= left_speed:
                    ramped_left_speed -= 1

            if right_speed > 0:
                if ramped_right_speed <= right_speed:
                    ramped_right_speed += 1
            else:
                if ramped_right_speed >= right_speed:
                    ramped_right_speed -= 1

            #print(ramped_left_speed, ramped_right_speed)
            drive.set_left_speed(ramped_left_speed)
            drive.set_right_speed(ramped_right_speed)

            # Check button change
            button_input = controller.snes_input()

        previous_input = button_input
        #print("previous input : " + previous_input)

finally:
    drive.cleanup()
