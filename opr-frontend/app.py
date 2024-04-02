from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/save_markers', methods=['POST'])
def save_markers():
    markers = json.loads(request.form['markers'])
    markers_with_index = {i: marker for i, marker in enumerate(markers)}
    with open('markers.json', 'w') as f:
        json.dump(markers_with_index, f)
    return jsonify({'success': True})


@app.route('/view_markers')
def view_markers():
    with open('markers.json', 'r') as f:
        markers = json.load(f)
    return render_template('view_markers.html', markers=markers)


if __name__ == '__main__':
    app.run(debug=True)
