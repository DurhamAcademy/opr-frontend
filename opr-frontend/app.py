from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import json

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('view_markers'))


@app.route('/edit_marker', methods=['POST'])
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
    return redirect(url_for('view_markers'))


@app.route('/backup_markers')
def backup_markers():
    filename = 'markers.json'
    filepath = '/markers.json'
    return send_file(filename, as_attachment=True)


@app.route('/deploy_markers')
def deploy_markers():
    print("test")
    # Need a function to copy the markers.json file to the robot where
    # running program is able to start using them.
    return redirect(url_for('view_markers'))


@app.route('/view_markers')
def view_markers():
    with open('markers.json', 'r') as f:
        markers = json.load(f)
    return render_template('view_markers.html', markers=markers)


if __name__ == '__main__':
    app.run(debug=True)
