from flask import (Flask,
                   render_template,
                   request,
                   jsonify,
                   redirect,
                   url_for,
                   send_file,
                   send_from_directory,
                   flash)
from flask_simplelogin import SimpleLogin, login_required, is_logged_in
import json
import time
import os
import dotenv
from werkzeug.utils import secure_filename
from fileinput import filename
import datetime
from flask_socketio import SocketIO, send, emit
import subprocess
import hashlib
import psutil
from robot_code import drive_client

app = Flask(__name__,
            template_folder='templates')
socketio = SocketIO(app,
                    cors_allowed_origins='*')

# Try to get secret from .env else set default.
try:
    dotenv.load_dotenv(dotenv_path='.env')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SIMPLELOGIN_USERNAME'] = os.getenv('SIMPLELOGIN_USERNAME')
    app.config['SIMPLELOGIN_PASSWORD'] = os.getenv('SIMPLELOGIN_PASSWORD')
    base_dir = os.getenv('OPR_BASE_DIR')
except:
    app.config['SECRET_KEY'] = 'something-secret'
    app.config['SIMPLELOGIN_USERNAME'] = 'admin'
    app.config['SIMPLELOGIN_PASSWORD'] = 'secret'
    base_dir = "./"

SimpleLogin(app)

# Globals
# Start Robot Code by Default
try:
    #robot_code_process = subprocess.Popen(["python", "robot_code/main.py"])
    robot_code_process = None
except:
    robot_code_process = None

drive = None
# Connect to drive controller
try:
    drive = drive_client.SocketClient()
    drive.connect()
except:
    print("not connected to drive controller")


# Check running processes.
def process_status(process_id):
    for process in psutil.process_iter(['pid', 'name']):
        if process.pid == process_id:
            return True
    return False


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def home():
    return redirect(url_for('view_markers'))


@app.route('/edit_marker', methods=['POST'])
@login_required
def edit_marker():
    # open markers file
    with open(base_dir + 'opr-frontend/markers.json', 'r') as f:
        markers = json.load(f)
    # update with new data
    for i in markers:
        if i == request.form['markerId']:
            markers[i]['name'] = request.form['markerName']
            markers[i]['heading'] = request.form['markerHeading']
            markers[i]['duration'] = request.form['markerDuration']
    # save back to file
    with open(base_dir + 'opr-frontend/markers.json', 'w') as f:
        json.dump(markers, f)
    return redirect(url_for('view_markers'))


@app.route('/save_markers', methods=['POST'])
@login_required
def save_markers():
    markers = json.loads(request.form['markers'])
    # re-index markers
    new_index = 0
    new_markers = {}
    for i in markers:
        temp = markers[i]
        new_markers[new_index] = temp
        new_index += 1
    with open(base_dir + 'opr-frontend/markers.json', 'w') as f:
        json.dump(new_markers, f, indent=4)
    return redirect(url_for('view_markers') + "?saved=true")


@app.route('/backup_markers')
@login_required
def backup_markers():
    filename = 'markers.json'
    filepath = '/markers.json'
    return send_file(filename, as_attachment=True)


@app.route('/deploy_markers')
@login_required
def deploy_markers():
    try:
        with open(base_dir + 'opr-frontend/markers.json', 'r') as f:
            markers = json.load(f)
        f.close()
        deploy = {}
        coordinates = []
        for i in markers:
            # set some defaults
            label = str(markers[i]['name'])
            duration = int(markers[i]['duration'])
            heading = int(markers[i]['heading'])
            coords = str(markers[i]['lat']) + "," + str(markers[i]['lng'])
            # put in a dict
            tmp = {'label': label,
                   'coordinates': coords,
                   'final_heading': heading,
                   'duration': duration
                   }
            #add dict to list
            coordinates.append(tmp)

        # assign to coordinates dict
        deploy['coordinates'] = coordinates

        # save to file
        with open(base_dir + 'opr-frontend/deploy.json', 'w') as f:
            f.write(json.dumps(deploy))
        f.close()

        # save to robot
        with open(base_dir + 'opr-frontend/robot_code/route.json', 'w') as f:
            f.write(json.dumps(deploy))
        f.close()

        return redirect(url_for('view_markers') + "?deployed=true")
    except:
        return redirect(url_for('view_markers') + "?deployed=false")


@app.route('/view_markers')
@login_required
def view_markers():
    global robot_code_process

    # read markers file
    with open('markers.json', 'r') as f:
        markers = json.load(f)
    f.close()

    try:
        # read current location from cgbot code
        with open(base_dir + 'opr-frontend/robot_code/gps_location.txt', 'r') as l:
            d = l.read()
        l.close()
        gps_location = eval(d)
    except:
        gps_location = (0, 0)

    # read current enviroment from cgbot code
    try:
        with open(base_dir + 'opr-frontend/robot_code/internal_temp_humidity.json', 'r') as thv:
            d = thv.read()
        thv.close()
        thvd = json.loads(d)
        temperature = thvd['temp']
        humidity = thvd['humidity']
        voltage = thvd['voltage']
    except:
        temperature = "?"
        humidity = "?"
        voltage = "?"

    try:
    # read status
        with open(base_dir + 'opr-frontend/robot_code/last_status.txt', 'r') as statusfile:
            status = statusfile.read()
        statusfile.close()
    except:
        status = "unknown-error"

    # read current schedule
    with open(base_dir + 'opr-frontend/robot_code/gps_schedule.json', 'r') as s:
        sched = json.load(s)
    s.close()

    # check for running code
    try:
        if process_status(robot_code_process.pid):
            robot_code = robot_code_process.pid
        else:
            robot_code = 0
    except:
        robot_code = 0

    return render_template('view_markers.html',
                           markers=markers,
                           gps_location=gps_location,
                           schedule_start=sched["begin"],
                           schedule_end=sched["end"],
                           schedule_enabled=sched["enabled"],
                           temperature=temperature,
                           humidity=humidity,
                           voltage=voltage,
                           status=status,
                           robot_code_pid=robot_code)


@app.route('/upload_markers', methods=['POST'])
@login_required
def upload_markers():
    if request.method == 'POST':
        f = request.files['markers']
        if f.filename == 'markers.json':
            f.save(f.filename)
        return redirect(url_for('view_markers'))


@app.route('/save_time', methods=['POST'])
@login_required
def save_time():
    if request.method == 'POST':
        j = {
            "begin" : request.form['begintime'],
            "end" : request.form['endtime'],
        }
        if 'enabled' in request.form:
            j["enabled"] = "on"
        else:
            j["enabled"] = "off"

        with open(base_dir + 'opr-frontend/robot_code/gps_schedule.json', 'w') as f:
            f.write(json.dumps(j))
        f.close()

        return redirect(url_for('view_markers'))


@app.route('/download_log', methods=['POST'])
@login_required
def download_log():
    date = request.form['date']
    print(date)
    logfile = "/var/log/cgbot-opr/log_" + str(date) + ".txt"
    if os.path.isfile(logfile):
        return send_file(logfile, as_attachment=True)
    else:
        return redirect(url_for('view_markers'))


@app.route('/enable_robot_code', methods=['GET'])
@login_required
def enable_robot_code():
    global robot_code_process
    robot_code_process = subprocess.Popen(["sudo", "python", "robot_code/main.py"])
    return redirect(url_for('view_markers'))


@app.route('/disable_robot_code', methods=['GET'])
@login_required
def disable_robot_code():
    global robot_code_process
    try:
        if robot_code_process.terminate():
            robot_code_process = robot_code_process.pid
    except:
        print("Unable to stop robot_code")

    return redirect(url_for('view_markers'))


@app.route('/remote_control')
@login_required
def remote_control():
    return render_template('remote_control.html', methods=['GET'])


@app.route('/move_robot', methods=['GET'])
@login_required
def move_robot():
    global drive
    direction = request.args.get('direction', default="none")
    if direction == 'forward':
        drive.send_command("forward")
    if direction == 'reverse':
        drive.send_command("reverse")
    if direction == 'left':
        drive.send_command("left")
    if direction == 'right':
        drive.send_command("right")
    if direction == 'stop':
        drive.send_command("stop")
    return "Done"


if __name__ == '__main__':
    app.run(debug=True)
    #socketio.run(app,
                 # host='0.0.0.0',
                 # port=5000,
                 # allow_unsafe_werkzeug=True)
