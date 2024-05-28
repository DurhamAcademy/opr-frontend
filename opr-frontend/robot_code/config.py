# Map all tunable vars in a single shared space.

# motor stuff
motor_left_direction_pin = 17
motor_right_direction_pin = 27
motor_left_speed_pin = 13
motor_right_speed_pin = 12
drive_speed = 100
drive_speed_turning = 30
# what pin is the safety light on?
safety_light_pin = 22
# pin for charger plug sensor.
charge_plug_sensor = 16
# how long after the last movement before we turn the light off?
safety_light_timeout = 20
# camera enable IO pin - Alarm1 input on camera
camera_io_alarm_pin = 6
# what pin is the physical switch that enters gps/controller mode on?
gps_mode_switch_pin = 24
# when using the mag how many degrees offset from the gps is it?
mag2gps_degree_offset = -20
# how many degrees in the heading are close enough to be accurate
turning_degree_accuracy = 7
# what is considered to low in battery voltage to continue functioning?
voltage_min_threshold = 9
# how long to drive forward before checking heading again.
gps_heading_check_interval = 5
# how often to read the ultrasonic sensors
ultrasonic_check_interval = 3
# how often to save gps coords, temp, and humidity to text files for frontend.
frontend_store_data_interval = 8
# how close the ultrasonics can read without triggering
ultra_alert_distance = 30
# accepted distance from desired point
point_radius_meters = 3.5
# how often to check the schedule in seconds
schedule_check_interval = 60
# how often to check low battery in seconds
battery_check_interval = 600
# maximum interior temperature
max_temperature = 100