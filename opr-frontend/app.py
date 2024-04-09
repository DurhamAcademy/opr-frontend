from flask import Flask, render_template, request, jsonify, redirect, url_for
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('view_markers.html')


@app.route('/edit_marker/<int:marker_id>')
def edit_marker(marker_id):
    # Fetch marker data based on the marker_id
    # You can pass the marker data to the template
    return render_template('edit_marker.html', marker_id=marker_id)


@app.route('/save_markers', methods=['POST'])
def save_markers():
    markers = json.loads(request.form['markers'])
    with open('markers.json', 'w') as f:
        json.dump(markers, f)
    return redirect(url_for('view_markers'))


@app.route('/view_markers')
def view_markers():
    with open('markers.json', 'r') as f:
        markers = json.load(f)
    return render_template('view_markers.html', markers=markers)


if __name__ == '__main__':
    app.run(debug=True)
