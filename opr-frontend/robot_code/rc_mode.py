import nes
import drive_client

controller = nes.Nes()
drive = drive_client.SocketClient()
drive.connect()

try:
    previous_input = "neutral"
    while True:
        button_input = controller.snes_input()

        while button_input != previous_input:
            if button_input == "up":
                drive.send_command("forward")
            elif button_input == "down":
                drive.send_command("reverse")
            elif button_input == "left":
                drive.send_command("left")
            elif button_input == "right":
                drive.send_command("right")

            # Check button change
            button_input = controller.snes_input()

        # Stop motors once if we go to neutral
        if button_input == "neutral" and previous_input != "neutral":
            drive.send_command("stop")

        previous_input = button_input
except:
    print("something went wrong")