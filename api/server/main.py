from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify, abort, request

from .utils import logger
from .utils.client import ModelClient


app = Flask(__name__)

app.config.from_object('server.config.default')
app.config.from_envvar('SERVER_APP_CONFIG', silent=True)

logger.initialize(app)
model_client = ModelClient(app.config['REDIS_HOST'])


@app.route('/')
@app.route('/api')
def home():
    return jsonify(success=True, message='Send files to /api/predict')


@app.route('/api/predict', methods=['POST'])
def predict():
    timeout = app.config.get('PREDICTION_TIMEOUT')

    try:
        img = request.files['image']
        app.logger.info(f'Received image {img.filename}')
        predictions = model_client.predict(img.stream, timeout)
        app.logger.info(f'Done processing image {img.filename}')
    except KeyError:
        abort(400, description='No image found.')
    except TimeoutError:
        abort(500, description='The model server does not respond.')
    except:
        app.logger.exception('Unexpected error:')
        abort(500)

    return jsonify(success=True, message=predictions)


@app.errorhandler(HTTPException)
def handle_error(err):
    app.logger.error(f'{request.url} {err.code} {err.name}')

    response = {
        'success': False,
        'message': err.description,
        'url': request.url
    }

    return jsonify(response), err.code

