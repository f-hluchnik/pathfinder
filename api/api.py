from flask import Flask
from flask import jsonify
from flask import request
from utils.FileUtils import parse_gpx_file, read_gpx_points
from App import App
from PathfinderApp import PathfinderApp

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    return "Pathfinder"


@app.route('/test/<int:number>', methods=['GET'])  # TODO: testing endpoint, remove for prod
def count(number):
    return jsonify({
        "plus 1": number + 1,
        "plus 2": number + 2
    })


@app.route('/points/', methods=['POST'])
def upload():
    file = request.files.get('file')
    try:
        parse_gpx_file(file)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'success': 'upload successful'}), 201


@app.route('/points/', methods=['GET'])
def get_points():
    points = read_gpx_points()
    return points


@app.route('/method/<string:method_type>', methods=['POST'])
def set_method(method_type):
    try:
        pathfinder.set_method(method_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    else:
        return jsonify({'success': 'method set successfully'}), 201


@app.route('/compute/', methods=['GET'])
def compute():
    compute_app = App()
    result = compute_app.compute()
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    pathfinder = PathfinderApp()
