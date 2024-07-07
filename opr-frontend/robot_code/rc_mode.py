import nes
import drive_client

controller = nes.Nes()
drive = drive_client.SocketClient()
drive.connect()

previous_input = "neutral"
while True:
    try:
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
            elif button_input == "neutral":
                drive.send_command("stop")

            previous_input = controller.snes_input()
    except:
        print("something went wrong")