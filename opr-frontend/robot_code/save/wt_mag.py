import serial
import pywitmotion
import math
import config


class Mag():
    """
    Class to read WitMotion Mag sensor.
    Keeping this in a class seems to help keep serial port open.
    """
    def __init__(self):
        self.ser = serial.Serial(config.witmotion_imu_path, config.witmotion_imu_baud_rate, timeout=5)
        self.x = self.ser.read()

    def calculate_heading(self, x, y):
        heading_rad = math.atan2(y, x)
        heading_deg = math.degrees(heading_rad)
        # Adjust for declination if necessary
        # declination = <your declination value in degrees>
        # heading_deg += declination
        # Normalize to range [0, 360)
        heading_deg = (heading_deg + 360) % 360
        return heading_deg

    def get_heading(self):
            s = self.ser.read_until(b'U')
            q = pywitmotion.get_magnetic(s)
            # q = wit.get_magnetic(msg)
            # q = wit.get_angle(msg)
            # q = wit.get_gyro(msg)
            # q = wit.get_acceleration(msg)
            if q is not None:
                return self.calculate_heading(q[1], q[0])