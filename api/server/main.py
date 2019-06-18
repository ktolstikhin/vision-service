from flask import Flask, jsonify, abort, request

from .utils.client import ModelClient
from .utils.logger import init_logger


app = Flask(__name__)

app.config.from_object('server.config.default')
app.config.from_envvar('SERVER_APP_CONFIG', silent=True)
init_logger(app)

model_client = ModelClient(redis_host='redis')


@app.route('/')
@app.route('/api')
def index():
    return jsonify(success=True, message='Send files to /api/predict')


@app.route('/api/predict', methods=['POST'])
def predict():
    timeout = app.config.get('PREDICTION_TIMEOUT')

    try:
        img = request.files['image']
        app.logger.info('Received image {}'.format(img.filename))
        predictions = model_client.predict(img.stream, timeout)
        app.logger.info('Done processing image {}'.format(img.filename))
    except KeyError:
        app.logger.error('Failed to process request: No image found.')
        abort(400, description='No image found.')
    except TimeoutError:
        app.logger.error('Failed to get predictions from the model server.')
        abort(500, description='The model server does not respond.')
    except:
        app.logger.exception('Unexpected error:')
        abort(500)

    return jsonify(success=True, message=predictions)


@app.errorhandler(400)
def bad_request(error):
    return jsonify(success=False, message=error.description), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify(success=False, message=error.description), 404


@app.errorhandler(405)
def not_allowed(error):
    return jsonify(success=False, message=error.description), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify(success=False, message=error.description), 500

