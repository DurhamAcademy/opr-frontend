from flask import Flask, render_template, request, jsonify, redirect, url_for
import json

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('view_markers'))


@app.route('/edit_marker/<int:marker_id>')
def edit_marker(marker_id):
    return render_template('edit_marker.html', marker_id=marker_id)


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


@app.route('/view_markers')
def view_markers():
    with open('markers.json', 'r') as f:
        markers = json.load(f)
    return render_template('view_markers.html', markers=markers)


if __name__ == '__main__':
    app.run(debug=True)
