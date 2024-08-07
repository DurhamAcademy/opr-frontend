import gps
import arduino
from dotenv import load_dotenv
import logging
import datetime
import time
import os
import json
import config
import threading
import camera
import charge_port
import drive_client
import lidar

# Import env file
load_dotenv()
load_dotenv(dotenv_path='../.env')
base_dir = os.getenv('OPR_BASE_DIR')

ar = arduino.Arduino()

l = lidar.RPLidarProcess()
l.get_angles()

drive_controller = drive_client.SocketClient()
drive_controller.connect()


"""
Logging
TODO: Setup logrotate on this directory.
"""
if not os.path.isdir("/var/log/cgbot-opr"):
    os.makedirs("/var/log/cgbot-opr")

logfile = "/var/log/cgbot-opr/log_" + str(datetime.date.today()) + ".txt"
logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


def log(text, logonly=False):
    """
    Write to logfile and console.
    :param logonly:
    :param text:
    :return: none
    """
    logging.debug(text)
    if not logonly:
        with open(base_dir + 'opr-frontend/robot_code/last_status.txt', 'w') as f:
            f.write(str(text))
        f.close()
    print(text)


def num_to_range(num, inMin, inMax, outMin, outMax):
    """
    Map values from one range to the next.
    :param num: value to find 
    :param inMin: input range min
    :param inMax: input range max
    :param outMin: output range min
    :param outMax: output range max
    :return: result
    """""
    return outMin + (float(num - inMin) / float(inMax - inMin) * (outMax - outMin))


def within_range_degrees(number, target, tolerance=config.turning_degree_accuracy):
    """"
    Check if a degree is withing a certian range
    """
    # Normalize numbers to be within the range of [0, 360)
    number = (number + 360) % 360
    target = (target + 360) % 360
    # Check if the absolute difference is within the tolerance range
    return abs(target - number) <= tolerance or abs(target - number + 360) <= tolerance


def get_routes():
    """
    Load routes from json
    :return: routes
    """
    with open(base_dir + 'opr-frontend/robot_code/route.json') as route_file:
        route = json.load(route_file)
    return route


def angle_check():
    """
    Check if something is in the way.
    Sections Left to Right.
    0: 270-315
    1: 316-359
    2: 0-45
    3: 46-90

    :return: number of the section affected.
    """
    ranges = [(270, 315), (316, 359), (0, 45), (46, 90)]
    angles = l.get_angles()

    largest_reading = [0, 0, 0, 0]

    for section in ranges:
        for angle in range(section[0], section[1] + 1):
            if 100 < angles[angle] < config.min_distance:
                if largest_reading[ranges.index(section)] < angles[angle]:
                    largest_reading[ranges.index(section)] = angles[angle]
    return largest_reading


def check_perimeter():
    """
    Adjust direction based on perimeter
    :return:
    """
    largest_reading = angle_check()

    if largest_reading[1] == 0 and largest_reading[2] == 0:
        # nothing in front, no course correction
        return
    elif (largest_reading[0] + largest_reading[1]) > (largest_reading[2] + largest_reading[3]):
        drive_controller.send_command("stop")
        log("course correction to left", logonly=True)
        time.sleep(1)
        # most room to move seems to be on left
        # move left
        # turn until there is no obstruction in front of section 2 which is slightly right of front.
        obstruction = angle_check()[2]
        while obstruction < config.min_distance:
            drive_controller.send_command("left")
            obstruction = angle_check()[2]
        return
    elif (largest_reading[0] + largest_reading[1]) < (largest_reading[2] + largest_reading[3]):
        drive_controller.send_command("stop")
        log("course correction to right", logonly=True)
        time.sleep(1)
        # most room seems to be on right
        # move right
        # turn until there is no obstruction in front of section 1 which is slightly left of front.
        obstruction = angle_check()[2]
        while obstruction < config.min_distance:
            drive_controller.send_command("right")
            obstruction = angle_check()[1]
        return


def fastest_direction(start_degree, end_degree):
    """
    Determines the fastest direction (left or right) from one degree to another
    on a 360-degree circle.

    Args:
        start_degree (float): Starting degree (0 to 359).
        end_degree (float): Ending degree (0 to 359).

    Returns: list
        [0] str: "left" if the fastest direction is to the left, "right" if to the right.
        [1] float: difference in degrees.
    """
    clockwise_distance = (end_degree - start_degree) % 360
    counterclockwise_distance = (start_degree - end_degree) % 360

    if clockwise_distance <= counterclockwise_distance:
        return ["left", counterclockwise_distance]
    else:
        return ["right", clockwise_distance]


def rotate_to_heading(current_heading, target_heading):
    """
    Rotate robot to face the correct heading.
    Appears to work.
    :param current_heading:
    :param target_heading:
    :return:
    """

    rotation_dir = fastest_direction(current_heading, target_heading)
    # rotation_dir[0] = the direction left/right
    # rotation_dir[1] = the amount of degrees the robot needs to move to get back on track.

    # only turn is more than ## degrees off.
    if rotation_dir[1] > config.turning_degree_accuracy:
        # What is current reading from compass?
        current_compass = (gps.get_heading()) % 360
        #print("start", current_compass)

        # Could consolidate with no ifs if you use negatives instead of left or right (-1 for left, 1 for right)
        # Would need to modify turn function to take in -35 to turn left
        if rotation_dir[0] == "left":
            log("Turning left for course correction", logonly=True)
            # What is the destination degrees on the compass in relation to target_heading? / subtract for left turn
            dest_compass = (current_compass - rotation_dir[1]) % 360
            # speed = num_to_range(rotation_dir[1], 0, 360, 30, 50)
            while not within_range_degrees(current_compass, dest_compass):
                d = drive_controller.send_command("left")
                print(d)
                current_compass = (gps.get_heading()) % 360
                #print("current: ", current_compass)
        else:
            # What is the destination degrees on the compass in relation to target_heading? / add for right turn
            dest_compass = (current_compass + rotation_dir[1]) % 360
            log("Turning right for course correction", logonly=True)
            # speed = num_to_range(rotation_dir[1], 0, 360, 30, 50)
            while not within_range_degrees(current_compass, dest_compass):
                drive_controller.send_command("right")
                current_compass = (gps.get_heading()) % 360
                #print("current: ", current_compass)
        # Stop the rotation and return.
        drive_controller.send_command("stop")
    else:
        print("rotation not needed.")


def go_to_position(target_pos: tuple):
    current_pos = gps.get_gps_coords()
    while abs(gps.haversine_distance(current_pos, target_pos)) > config.point_radius_meters:
        current_pos = gps.get_gps_coords()
        current_heading = gps.gps_heading()
        # Use heading from GPS to determine a target_heading to destination coordinates
        target_heading = gps.calculate_initial_compass_bearing(current_pos, target_pos)
        # print("targetheading: " + str(target_heading))
        rotate_to_heading(current_heading, target_heading)

        # Drive forward config.gps_heading_check_interval seconds. check perimeter every
        # .5 seconds.
        time_count = 0
        while time_count <= config.gps_heading_check_interval:
            check_perimeter()
            drive_controller.send_command("forward")

            time.sleep(.5)
            time_count += .5

    drive_controller.send_command("stop")


def check_obstacle():
    """
    Check the front of the robot to see if there is an obstacle.
    :return: True if obstacle is detected, False otherwise.
    """
    try:
        reading = ar.get_ultrasonic()
        if 40 < reading[0] < 100:
            return True
        if 40 < reading[1] < 100:
            return True
        else:
            return False
    except:
        return False


def check_stuck():
    """
    Need a function to check that the robot is not stuck.
    Something like has motors run and GPS coordinates are
    not changing.
    :return: Bool
    """
    return False


def check_perimeter():
    """
    Need a function to check that all onics are clear
    and nothing is around the robot.
    Return a side that is blocked
    :return: none, left, right, front, back
    """
    return "none"


def check_schedule():
    """
    Returns True if schedule permits robot to run GPS cycle,
    :return: True or False
    """
    try:
        with open(base_dir + 'opr-frontend/robot_code/gps_schedule.json', "r") as j:
            d = j.read()
            d = json.loads(d)
        j.close()
        start_time = datetime.datetime.strptime(d['begin'], '%H:%M').time()
        end_time = datetime.datetime.strptime(d['end'], '%H:%M').time()
        now_time = datetime.datetime.now().time()

        if d["enabled"] == 'on':
            if start_time < end_time:
                return now_time >= start_time and now_time <= end_time
            else:
                # Over midnight:
                return now_time >= start_time or now_time <= end_time
    except:
        return False


def check_battery():
    """
    False is battery is not weak
    False is good to go!
    :return: True or False
    """
    try:
        v = ar.get_voltage()
        if v > 0:
            if ar.get_voltage() <= config.voltage_min_threshold:
                return True
            else:
                return False
    except:
        return False


def check_temp():
    """
    True is good to go. Under temperature conditions.
    :return:
    """
    try:
        if ar.get_temperature() <= float(config.max_temperature):
            return True
        else:
            return False
    except:
        return True


def store_internal_enviro():
    """
    Store information about control box envirmoent in text file for frontend to read.

    :return: None
    """
    threading.Timer(config.frontend_store_data_interval, store_internal_enviro).start()
    try:
        j = {
            "temp": str(ar.get_temperature()),
            "humidity": str(ar.get_humidity()),
            "voltage": str(ar.get_voltage())
        }
        with open(base_dir + 'opr-frontend/robot_code/internal_temp_humidity.json', 'w') as f:
            f.write(json.dumps(j))
        f.close()
    except:
        log("Unable to store enviroment data")


def store_location():
    """
    Store current location to a text file for frontend.
    Since main.py owns the serial port there is no  better way to have this info shared.
    :return:
    """
    threading.Timer(config.frontend_store_data_interval, store_location).start()
    try:
        with open(base_dir + 'opr-frontend/robot_code/gps_location.txt', 'w') as f:
            f.write(str(gps.get_gps_coords()))
        f.close()
    except:
        log("Unable to store location")


def main():

    # Save location to file ever x seconds
    # Threading has it running on a schedule. Do not put in loop.
    store_location()

    # Save info about control box enviroment.
    # Threading has it running on a schedule. Do not put in loop.
    store_internal_enviro()

    ### some default vars ###
    # next battery check time in epoch
    next_battery_check = time.time()
    # next schedule check time in epoch
    next_schedule_check = time.time()

    """ 
    
    """
    try:
        while True:
            """
            Check Humidity and Temperature Level
            """

            """
            Check charging plug is not connected.
            """
            if charge_port.charge_port_status():
                log("Charging plug is connected! Pausing 10 Seconds.")
                time.sleep(10)
                continue

            """
            GPS Mode
            """

            """
            Check Battery Level
            If the battery is low, then lets set that var to True. 
            Later we will not stay at a location for "duration", and not continue on route.
            """
            # don't run route if the battery is low.
            if time.time() > next_battery_check:
                next_battery_check = time.time() + config.battery_check_interval
                if check_battery():
                    log("Battery too weak to begin new GPS route")
                    # Hold code here until we can check the battery again.
                    time.sleep(config.battery_check_interval + 5)
                    continue

            # check schedule
            if time.time() > next_schedule_check:
                next_schedule_check = time.time() + config.schedule_check_interval
                if not check_schedule():
                    log("Not scheduled for GPS")
                    continue

            # beginning of the route.
            if check_schedule():

                route = get_routes()
                for i in route['coordinates']:

                    # Do we have a valid signal?
                    gps_check = gps.get_gps_coords()
                    if gps_check[0] == 0.0 or gps_check[1] == 0.0:
                        log("No GPS Signal! Null Island.")
                        continue

                    log("Going to location: {}.".format(i['label']))
                    #log("Coordinates: {}.".format(i['coordinates']))

                    # convert to tuple
                    coordinates = eval(i['coordinates'])

                    # disable recording on camera
                    camera.disable_camera()

                    # go to the spot
                    go_to_position(coordinates)
                    log("Destination reached.!!!")

                    if check_battery():
                        # False is good.
                        log("Battery is low, not waiting at this location.")
                        continue

                    if not check_temp():
                        # True is good.
                        log("Control temp exceeded, not waiting at this location.")
                        continue

                    # rotate to heading for recording
                    current_heading = gps.gps_heading()
                    log("Rotate to final heading {}.".format(i['final_heading']))
                    rotate_to_heading(current_heading, i['final_heading'])

                    # wait to settle
                    time.sleep(3)

                    # enable camera for recording
                    log("Enabling Camera.")
                    camera.enable_camera()

                    # wait for the duration specified if battery not low.
                    today = datetime.datetime.now()
                    future_date = today + datetime.timedelta(seconds=int(i['duration']))
                    log("Waiting here for {} seconds until {}.".format(
                        str(i['duration']),
                        str(future_date.strftime('%I:%M:%S'))
                    ))
                    time.sleep(i['duration'])

                    log("Disabling Camera.")
                    camera.disable_camera()

    finally:
        log("Main loop complete.")
        camera.disable_camera()
        drive_controller.send_command("stop")


if __name__ == "__main__":
    main()
