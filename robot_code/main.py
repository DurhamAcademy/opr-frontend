import motor_driver
import gps
import arduino
import nes
from dotenv import load_dotenv
import logging
import datetime
import time
import os
import json
import config
import threading
import camera

# Import env file
load_dotenv()

controller = nes.Nes()
drive = motor_driver.Motor()
ar = arduino.Arduino()

"""
Logging
TODO: Setup logrotate on this directory.
"""
if not os.path.isdir("/var/log/cgbot-opr"):
    os.makedirs("/var/log/cgbot-opr")

logfile = "/var/log/cgbot-opr/log_" + str(datetime.date.today()) + ".txt"
logging.basicConfig(filename=logfile)
logging.basicConfig(level=logging.DEBUG)


def log(text):
    """
    Write to logfile and console.
    :param text:
    :return: none
    """
    logging.debug(text)
    with open('last_status.txt', 'w') as f:
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
    with open("route.json") as route_file:
        route = json.load(route_file)
    return route


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
        print("start", current_compass)

        # Could consolidate with no ifs if you use negatives instead of left or right (-1 for left, 1 for right)
        # Would need to modify turn function to take in -35 to turn left
        if rotation_dir[0] == "left":
            # What is the destination degrees on the compass in relation to target_heading? / subtract for left turn
            dest_compass = (current_compass - rotation_dir[1]) % 360
            # speed = num_to_range(rotation_dir[1], 0, 360, 30, 50)
            while not within_range_degrees(current_compass, dest_compass):
                drive.drive_turn_left(config.drive_speed_turning)
                current_compass = (gps.get_heading()) % 360
                print("current: ", current_compass)
        else:
            # What is the destination degrees on the compass in relation to target_heading? / add for right turn
            dest_compass = (current_compass + rotation_dir[1]) % 360
            print("dest", dest_compass)
            # speed = num_to_range(rotation_dir[1], 0, 360, 30, 50)
            while not within_range_degrees(current_compass, dest_compass):
                drive.drive_turn_right(config.drive_speed_turning)
                current_compass = (gps.get_heading()) % 360
                print("current: ", current_compass)
        # Stop the rotation and return.
        drive.drive_stop()
    else:
        print("rotation not needed.")


def simple_check(ultra):
    print(ultra)
    directions = [1, -1]  # 1 is right, -1 is left
    turn_dir = directions[ultra.index(max(ultra[:2]))]  # pick left direction if left ultra is greater, vice versa
    forward_time = 2
    orig_angle = gps.get_heading()
    for i in range(2):
        for j in range(2):
            # check two times if you can get around obstacle
            if turn_dir == 1:
                rotate_to_heading(orig_angle, orig_angle + 70)  # turn in chosen direction
            else:
                rotate_to_heading(orig_angle, orig_angle - 70)  # turn in chosen direction
            drive.drive_forward()
            time.sleep(forward_time)
            angle = gps.get_heading()
            print("back", orig_angle)
            rotate_to_heading(angle, orig_angle)  # turn back to check ultras
            check = ar.get_ultrasonic()
            print(check[:2])
            if min(check[:2]) > config.ultra_alert_distance or min(check[:2]) == 0:
                return True  # check ultrasonics, return true if they are clear
        turn_dir *= -1  # try the other direction, currently are facing towards obstacle
        angle = gps.get_heading()
        rotate_to_heading(angle, orig_angle + (90 * turn_dir))  # turn in new chosen direction in order to move back
        drive.drive_forward()
        time.sleep(forward_time * 2)  # drive back to where you started and repeat loop
    return False  # return false if you can't get unstuck, give up


def go_to_position(target_pos: tuple):
    current_pos = gps.get_gps_coords()
    while abs(gps.haversine_distance(current_pos, target_pos)) > config.point_radius_meters:
        current_pos = gps.get_gps_coords()
        current_heading = gps.gps_heading()
        # Use heading from GPS to determine a target_heading to destination coordinates
        target_heading = gps.calculate_initial_compass_bearing(current_pos, target_pos)
        print("targetheading: " + str(target_heading))
        rotate_to_heading(current_heading, target_heading)
        drive.drive_forward()
        print("start forward")
        time.sleep(1)
        print("stop forward")
    drive.drive_stop()


def check_stuck():
    """
    Need a function to check that the robot is not stuck.
    Something like has motors run and GPS coordinates are
    not changing.
    :return: Bool
    """
    return False


def reroute(trigger, distance):
    """
    Complex ultrasonic reroutes, unfinished
    """
    closer = "right"  # pos will make it turn right, neg will make it turn left
    if trigger[0] < trigger[1]:
        closer = "left"
    # reverse for distance
    if closer == "left":
        drive.set_left_speed(-30)
        drive.set_right_speed(-40)
    else:
        drive.set_left_speed(-40)
        drive.set_right_speed(-30)
    checkUltra = ar.get_ultrasonic()
    if checkUltra[:2] == 0:
        drive.drive_forward()
    elif checkUltra[1:] == 0:
        drive.drive_reverse()
    else:
        print("is there an else here")


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
        with open("gps_schedule.json", "r") as j:
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
    if ar.get_voltage() <= config.voltage_min_threshold:
        return True
    else:
        return False


def check_temp():
    if ar.get_temperature() <= config.max_temperature:
        return True
    else:
        return False


def store_internal_enviro():
    """
    Store information about control box envirmoent in text file for frontend to read.

    :return: None
    """
    threading.Timer(config.frontend_store_data_interval, store_internal_enviro).start()
    j = {
        "temp": str(ar.get_temperature()),
        "humidity": str(ar.get_humidity()),
        "voltage": str(ar.get_voltage())
    }
    with open('internal_temp_humidity.json', 'w') as f:
        f.write(json.dumps(j))
    f.close()


def store_location():
    """
    Store current location to a text file for frontend.
    Since main.py owns the serial port there is no  better way to have this info shared.
    :return:
    """
    threading.Timer(config.frontend_store_data_interval, store_location).start()
    with open('gps_location.txt', 'w') as f:
        f.write(str(gps.get_gps_coords()))
    f.close()


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
        # last_print = 0
        ultras = ar.get_ultrasonic()
        simple_check(ultras)
        print("done")
        while True:
            """
            Check safety light timeout
            TODO: Enable mutilthreading and move this into its own thread.
            """
            drive.safety_light_timeout()

            """
            Check Humidity and Temperature Level
            """

            """
            Drive mode
            """
            if controller.get_mode() == "controller":
                """
                Controller Mode
                """
                left_speed, right_speed = controller.wpm_controller(controller.snes_input())
                drive.set_left_speed(left_speed)
                drive.set_right_speed(right_speed)

                """
                If select button is pressed, print coordinates
                """
                if controller.snes_input() == "select":
                    try:
                        print(gps.get_gps_coords())
                        time.sleep(1)
                    except Exception as e:
                        print(e)

            else:
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
                    if not check_battery():
                        log("Battery too weak to begin new GPS route")
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
                        log("Going to location: {}.".format(i['label']))
                        log("Coordinates: {}.".format(i['coordinates']))

                        # convert to tuple
                        coordinates = eval(i['coordinates'])

                        # disable recording on camera
                        camera.disable_camera()

                        # go to the spot
                        go_to_position(coordinates)
                        log("Destination reached.!!!")

                        # rotate to heading for recording
                        current_heading = gps.gps_heading()
                        log("Rotate to final heading {}.".format(i['final_heading']))
                        rotate_to_heading(current_heading, i['final_heading'])

                        # enable camera for recording
                        camera.enable_camera()

                        if not check_battery() and not check_temp():
                            # wait for the duration specified if battery not low.
                            log("Waiting here for {} seconds.".format(str(i['duration'])))
                            time.sleep(i['duration'])
                        else:
                            log("Battery is low or temp exceeded, not waiting at this location.")


    finally:
        log("Main loop complete.")
        drive.cleanup()


if __name__ == "__main__":
    main()
