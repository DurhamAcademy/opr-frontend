#!/bin/sh

# Run updates each time
#arduino-cli core update-index
#arduino-cli board list
#arduino-cli core install arduino:avr
#arduino-cli core list

arduino-cli compile --fqbn  arduino:avr:mega arduino_opr_bot
arduino-cli upload -p /dev/serial/by-id/usb-Arduino__www.arduino.cc__0042_851393033313512102C2-if00 --fqbn  arduino:avr:mega arduino_opr_bot