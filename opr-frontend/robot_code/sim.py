import math
# import numpy as np
# import cv2
import time
# import gps
import folium

# field = np.zeros([1000, 1000, 3], dtype=np.uint8)

def update_map(m, current_pos, path, filename='pos_map.html'):
    # Draw a line from the previous position to the current position
    if len(path) > 0:
        folium.PolyLine(
            locations=[(path[-1][0], path[-1][1]), (current_pos[0], current_pos[1])],
            color='red'
        ).add_to(m)

    # Update the marker on the map
    """folium.Marker(
        location=[current_pos[0], current_pos[1]],
        popup=f'Current Position: {current_pos}',
        icon=folium.Icon(color='red')
    ).add_to(m)"""
    folium.Marker(
        location=[30.2664698, -97.73384],
        popup=f'Target Position: {35.266666, -94.733330}',
        icon=folium.Icon(color='red')
    ).add_to(robot_map)

    # Save the map to an HTML file
    m.save(filename)


def update_position(left_motor_speed, right_motor_speed, current_position, time_interval):
    # Constants for wheelbase and conversion factors
    wheelbase = 10.0  # Replace with the actual wheelbase of your robot
    distance_per_pulse = 0.1  # Replace with the actual distance traveled per pulse of your encoders

    # Calculate the distance traveled by each wheel in the time interval
    left_distance = left_motor_speed * time_interval * distance_per_pulse
    right_distance = right_motor_speed * time_interval * distance_per_pulse

    # Calculate the average distance traveled by the wheels
    avg_distance = (left_distance + right_distance) / 2.0

    # Calculate the change in angle (in radians)
    delta_theta = (right_distance - left_distance) / wheelbase

    # Calculate the new heading of the robot with 0 degrees meaning exactly north
    new_heading = (current_position[2] - math.degrees(delta_theta)) % 360

    # Calculate the new position of the robot in GPS coordinates
    earth_radius = 6371000.0  # Earth's radius in meters
    latitude_scale = math.radians(current_position[0])  # Scale for latitude conversion

    temp_heading = new_heading
    new_latitude, new_longitude = update_coordinates(position[0], position[1], avg_distance, new_heading)

    # Return the updated position as a tuple (latitude, longitude, heading)
    return new_latitude, new_longitude, new_heading



def update_coordinates(latitude, longitude, distance, heading):
    # Earth radius in kilometers
    earth_radius = 6371.0

    # Convert heading to radians
    heading_rad = math.radians(heading)

    # Convert distance to kilometers
    distance_km = distance / 1000.0

    # Calculate new latitude and longitude
    # new_latitude = math.degrees(math.asin(math.sin(math.radians(latitude)) * math.cos(distance_km / earth_radius) + math.cos(math.radians(latitude)) * math.sin(distance_km / earth_radius) * math.cos(heading_rad))))
    new_latitude = math.degrees(math.asin(math.sin(math.radians(latitude)) * math.cos(distance_km / earth_radius) + math.cos(math.radians(latitude)) * math.sin(distance_km / earth_radius) * math.cos(heading_rad)))
    new_longitude = math.degrees(math.radians(longitude) + math.atan2(math.sin(heading_rad) * math.sin(distance_km / earth_radius) *
                                               math.cos(math.radians(latitude)),
                                               math.cos(distance_km / earth_radius) - math.sin(math.radians(latitude)) *
                                               math.sin(math.radians(new_latitude))))

    return new_latitude, new_longitude

def draw_bot(position):
    cv2.circle(field, (int(position[0]), int(position[1])), 10, (255, 0, 0), -1)
    end_x = int(position[0] + 20 * math.cos(position[2] * math.pi / 180))
    end_y = int(position[1] + 20 * math.sin(position[2] * math.pi / 180))
    cv2.line(field, (int(position[0]), int(position[1])), (end_x, end_y), (0, 255, 255), 2)
    cv2.imshow("Field", field)
    cv2.waitKey(1)

def rotate_to_heading(current_heading, target_heading):
    global position
    # Calculate difference between current and target heading
    # Adjust the following formula based on your specific robot setup
    heading_difference = (target_heading - current_heading) % 360
    # rotate left by default
    rotation_dir = 1 if heading_difference <= 180 else -1
    print(rotation_dir)
    current_heading = position[2]
    print(target_heading)
    print(current_heading)
    while abs(target_heading - current_heading) > 1:
        # rotate until real heading is close to target heading
        # motor_driver.set_left_speed(-50 * rotation_dir)
        # motor_driver.set_right_speed(50 * rotation_dir)
        position = update_position(-50 * rotation_dir, 50 * rotation_dir, position, 0.5)
        current_heading = position[2]
        # update heading and rerun loop
        # _, current_heading = gps.get_gps_coords()
        # input()
    print("finished turning. current degrees:", current_heading)

    position = update_position(30, 30, position, 0.5)
    # Set motor speeds using PWM
    # motor_driver.set_left_speed(20)
    # motor_driver.set_right_speed(20)

    # Move in a straight line for a specified duration
    time.sleep(0.5)  # Adjust the duration as needed


position = (30.266666, -97.733330, 0)
time_interval = 5
robot_map = folium.Map(location=[position[0], position[1]], max_zoom=60, zoom_start=35)
path = []  # List to store the path
folium.Marker(
    location=[35.977669299999995, -78.9698552],
    popup=f'Target Position: {35.977669299999995, -78.9698552}',
    icon=folium.Icon(color='red')
).add_to(robot_map)

def go_to_position(target_pos: tuple):
    # current_pos, current_heading = gps.get_gps_coords()
    global position
    current_pos = (position[0], position[1])
    current_heading = position[2]
    """for i in range(10):
        position = update_position(50, 50, position, 5)
        update_map(robot_map, position, path)

        # Update the previous position for the next iteration
        prev_position = position

        # Append the current position to the path
        path.append((position[0], position[1]))
        time.sleep(2)
        print(position)"""
    while gps.haversine_distance(current_pos, target_pos) > 1:
        # current_pos, current_heading = gps.get_gps_coords()
        current_pos = (position[0], position[1])
        current_heading = position[2]
        path.append((position[0], position[1]))
        update_map(robot_map, position, path)
        print(path)
        draw_bot(position)

        print("thingie", current_pos, target_pos)
        target_heading = gps.calculate_heading(current_pos, target_pos)
        print("tar", target_heading)
        rotate_to_heading(current_heading, target_heading)


# position = (field.shape[1] / 2, field.shape[0] / 2, 0.0)

# cv2.circle(field, (700, 500), 10, (0, 0, 255), -1)
# go_to_position((30.2664698, -97.73384))
"""for i in range(30):
    position = update_position()"""

# cv2.imshow("Field", field)
# cv2.waitKey(0)
