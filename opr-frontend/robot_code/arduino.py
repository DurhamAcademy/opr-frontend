import serial
import time
import threading
import config

"""
Example data from Arduino:
$ = Begin of line
\r\n = EOL
$34|23|12|34|30.0|50.0|12.1\r\n
$Ultrasonic1|Ultrasonic2|Ultrasonic3|Ultrasonic4|Temp|Hunid|Voltage\r\n
"""


class Arduino:

    def __init__(self):
        self.ser = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0042_851393033313512102C2-if00',
                                 9600,
                                 timeout=1
                                 )
        self.ser.reset_input_buffer()
        self.ultrasonic_last_check = 0.00

    def read_data(self, val):
        # don't try more than 4 times
        for i in range(0, 3, 1):
            try:
                # is this needed?
                self.ser.reset_input_buffer()
                data = self.ser.readline()
                d = data.decode()
                if d[0] == "$":
                    d = d[1:]
                    dd = d.split("|")
                    if val == 0:
                        return [dd[0], dd[1], dd[2], dd[3]]
                    else:
                        return dd[int(val)]
                else:
                    # not a new line from arduino, try again
                    continue
            except:
                continue
        return "error"

    def get_temperature(self):
        """
        Reads the temperature from the Arduino. Returns the temperature in degrees Celsius.
        :return: float degrees
        """
        return float(self.read_data(4))

    def get_humidity(self):
        """
        Reads the humidity from the Arduino. Returns the humidity as float.
        :return: float humidity
        """
        return float(self.read_data(5))

    def get_voltage(self):
        """
        Reads the voltage from Battery through the Arduino. Returns the voltage as float.
        :return: float voltage
        """
        return float(self.read_data(6))

    def get_ultrasonic(self):
        """
        Reads the ultrasonic sensors from the Arduino. Returns the ultrasonic as
        :return: list
        """
        self.ultrasonic_last_check = time.time()
        ints = [int(x) for x in self.read_data(0)]
        return ints
