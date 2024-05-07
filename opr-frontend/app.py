from flask import (Flask,
                   render_template,
                   request,
                   jsonify,
                   redirect,
                   url_for,
                   send_file,
                   send_from_directory,
                   flash)
from flask_simplelogin import SimpleLogin, login_required
import json
import os
import dotenv
from werkzeug.utils import secure_filename
from fileinput import filename


app = Flask(__name__)

# Try to get secret from .env else set default.
try:
    dotenv.load_dotenv(dotenv_path='.env')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SIMPLELOGIN_USERNAME'] = os.getenv('SIMPLELOGIN_USERNAME')
    app.config['SIMPLELOGIN_PASSWORD'] = os.getenv('SIMPLELOGIN_PASSWORD')
except:
    app.config['SECRET_KEY'] = 'something-secret'
    app.config['SIMPLELOGIN_USERNAME'] = 'admin'
    app.config['SIMPLELOGIN_PASSWORD'] = 'secret'

SimpleLogin(app)


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
    with open('markers.json', 'r') as f:
        markers = json.load(f)
    # update with new data
    for i in markers:
        if i == request.form['markerId']:
            markers[i]['name'] = request.form['markerName']
            markers[i]['heading'] = request.form['markerHeading']
            markers[i]['duration'] = request.form['markerDuration']
    # save back to file
    with open('markers.json', 'w') as f:
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
    with open('markers.json', 'w') as f:
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
        with open('markers.json', 'r') as f:
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
        with open('deploy.json', 'w') as f:
            f.write(json.dumps(deploy))
        f.close()

        # save to robot
        with open('../../cgbot-opr/route.json', 'w') as f:
            f.write(json.dumps(deploy))
        f.close()

        return redirect(url_for('view_markers') + "?deployed=true")
    except:
        return redirect(url_for('view_markers') + "?deployed=false")


@app.route('/view_markers')
@login_required
def view_markers():
    # read markers file
    with open('markers.json', 'r') as f:
        markers = json.load(f)
    f.close()
    # read current location from cgbot code
    with open('../../cgbot-opr/gps_location.txt', 'r') as l:
        d = l.read()
    l.close()
    gps_location = eval(d)

    # read current enviroment from cgbot code
    with open('../../cgbot-opr/internal_temp_humidity.json', 'r') as thv:
        d = thv.read()
    thv.close()
    thvd = json.loads(d)
    temperature = thvd['temp']
    humidity = thvd['humidity']
    voltage = thvd['voltage']

    # read status
    with open('../../cgbot-opr/last_status.txt', 'r') as statusfile:
        status = statusfile.read()
    statusfile.close()

    # read current schedule
    with open('../../cgbot-opr/gps_schedule.json', 'r') as s:
        sched = json.load(s)
    s.close()

    return render_template('view_markers.html',
                           markers=markers,
                           gps_location=gps_location,
                           schedule_start=sched["begin"],
                           schedule_end=sched["end"],
                           schedule_enabled=sched["enabled"],
                           temperature=temperature,
                           humidity=humidity,
                           voltage=voltage,
                           status=status)


@app.route('/upload_markers', methods=['POST'])
def upload_markers():
    if request.method == 'POST':
        f = request.files['markers']
        if f.filename == 'markers.json':
            f.save(f.filename)
        return redirect(url_for('view_markers'))


@app.route('/save_time', methods=['POST'])
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

        with open('../../cgbot-opr/gps_schedule.json', 'w') as f:
            f.write(json.dumps(j))
        f.close()

        return redirect(url_for('view_markers'))


if __name__ == '__main__':
    app.run(debug=True)
