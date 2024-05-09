import folium
from IPython.display import display, HTML
import math
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import time

# Initialize the map with the initial position of the robot
initial_position = (37.7749, -122.4194, 0.0)  # Initial position (latitude, longitude, heading)
robot_map = folium.Map(location=[initial_position[0], initial_position[1]], zoom_start=15)

# Create a marker for the initial position
folium.Marker(
    location=[initial_position[0], initial_position[1]],
    popup='Initial Position',
    icon=folium.Icon(color='blue')
).add_to(robot_map)

# Display the initial map
display(robot_map)

# Initialize an empty plot for the heading arrow
fig, ax = plt.subplots(figsize=(3, 3))
arrow = ax.arrow(0, 0, 0, 0, head_width=0.1, head_length=0.1, fc='red', ec='red')

# Function to draw the robot on the map and update the heading arrow
def draw_bot(m, current_pos):
    # Draw a line from the previous position to the current position
    folium.PolyLine(
        locations=[(current_pos[0], current_pos[1])],
        color='red'
    ).add_to(m)

    # Update the marker on the map
    folium.Marker(
        location=[current_pos[0], current_pos[1]],
        popup=f'Current Position: {current_pos}',
        icon=folium.Icon(color='red')
    ).add_to(m)

    # Remove the previous arrow
    plt.cla()

    # Create a new arrow representing the heading
    arrow = plt.arrow(
        current_pos[0], current_pos[1],
        0.1 * math.cos(current_pos[2]), 0.1 * math.sin(current_pos[2]),
        color='red',
        width=0.01,
        head_width=0.05
    )

    # Refresh the map display
    display(m)

# Example loop for updating position in a simulated robot movement
prev_position = initial_position
time_interval = 0.1  # Time interval for each iteration (adjust as needed)

for _ in range(10):  # Example loop for 50 iterations
    # Replace these values with the actual GPS coordinates from your robot
    current_position = (37.7749 + 0.001 * _, -122.4194 + 0.001 * _, 0.0)

    # Draw the robot on the map and update the heading arrow
    draw_bot(robot_map, current_position)

    # Update the previous position for the next iteration
    prev_position = current_position

    # Sleep for a short interval to simulate real-time updates
    time.sleep(time_interval)
plt.show()