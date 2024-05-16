from robot_code import config
import time
import subprocess
import RPi.GPIO as GPIO

frontend_process = None
manual_process = None
last_mode = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(config.gps_mode_switch_pin, GPIO.IN)
"""
Daemon
Switches between GPS mode and manual mode. Based on physical switch

Install to /lib/systemd/system/opr.service as:
[Unit]
Description=opr-frontend
After=multi-user.target

[Service]
User=root
WorkingDirectory=/home/pi/opr-frontend/opr-frontend
ExecStart=/usr/bin/python daemon.py

[Install]
WantedBy=multi-user.target

Once installed - start with -> sudo systemctl start opr-frontend.service
To start up at boot -> sudo systemctl enable opr-frontend.service

"""
while True:
    if GPIO.input(config.gps_mode_switch_pin) == 1 and (last_mode == 0 or last_mode == 2):
        last_mode = 1
        # GPS Mode

        # Stop Manual Mode
        try:
            print("Stopping manual RC mode service.")
            manual_process.terminate()
        except:
            print("Failed or nothing to terminate for manual process.")

        # Start Frontend
        try:
            print("Starting Frontend service with gunicorn.")
            frontend_process = subprocess.Popen(["/usr/local/bin/gunicorn", "app:app"])
        except:
            print("Failed to start frontend process.")

        continue

    elif GPIO.input(config.gps_mode_switch_pin) == 0 and (last_mode == 1 or last_mode == 2):
        last_mode = 0
        # Manual Mode
        try:
            print("Stopping Frontend service.")
            frontend_process.terminate()
        except:
            print("Failed or nothing to terminate for frontend process.")

        try:
            print("Starting manual RC mode service.")
            frontend_process = subprocess.Popen(["/usr/bin/python", "robot_code/enable_rc.py"])
        except:
            print("Failed to start manual process.")

        continue
    else:
        # Nothing to do. Pausing some.
        time.sleep(3)





