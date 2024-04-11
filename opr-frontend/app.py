from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_simplelogin import SimpleLogin, login_required
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'something-secret'
app.config['SIMPLELOGIN_USERNAME'] = 'admin'
app.config['SIMPLELOGIN_PASSWORD'] = 'secret'
SimpleLogin(app)

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
        json.dump(new_markers, f)
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
    return render_template('view_markers.html', markers=markers, gps_location=gps_location)


if __name__ == '__main__':
    app.run(debug=True)
