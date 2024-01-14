import logging

from flask import Flask, jsonify, request
from celery import Celery
from utils.FileUtils import parse_gpx_file
from PathfinderApp import PathfinderApp

app = Flask(__name__)
app.config.from_pyfile('celery_config.py')
celery = Celery(app.name, broker=app.config['BROKER_URL'])
celery.conf.update(app.config)


@celery.task
def background_computation(file_path: str, method_type: str, api_key: str):
    pathfinder = PathfinderApp(api_key)
    try:
        parse_gpx_file(file_path)
        pathfinder.set_method(method_type)
        pathfinder.compute()
    except Exception as e:
        return str(e)
    else:
        return {
            'success': 'operation completed successfully',
            'distance': pathfinder.distance,
            'points': pathfinder.points
        }


@app.route('/compute/', methods=['POST'])
def compute():
    file = request.files.get('file')
    method_type = request.form.get('method_type')
    api_key = request.form.get('api_key')

    # Save the file to a temporary location
    file_path = './tmp/points.gpx'
    file.save(file_path)

    task = background_computation.apply_async(args=[file_path, method_type, api_key])

    return jsonify({'task_id': task.id, 'status': 'processing'}), 202


@app.route('/result/<string:task_id>/', methods=['GET'])
def get_result(task_id):
    task = background_computation.AsyncResult(task_id)

    if task.state == 'SUCCESS':
        return jsonify({'status': task.state, 'result': task.result})
    elif task.state == 'FAILURE':
        return jsonify({'status': task.state, 'error': str(task.result)}), 500
    else:
        return jsonify({'status': task.state}), 202


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
