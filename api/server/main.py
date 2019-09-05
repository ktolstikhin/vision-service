from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify, abort, request

from .utils.client import ModelClient
from .utils.logger import init_logger


app = Flask(__name__)

app.config.from_object('server.config.default')
app.config.from_envvar('SERVER_APP_CONFIG', silent=True)
init_logger(app)

redis_host = app.config['REDIS_HOST']
model_client = ModelClient(redis_host)


@app.route('/')
@app.route('/api')
def home():
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
        abort(400, description='No image found.')
    except TimeoutError:
        abort(500, description='The model server does not respond.')
    except:
        app.logger.exception('Unexpected error:')
        abort(500)

    return jsonify(success=True, message=predictions)


@app.errorhandler(HTTPException)
def handle_error(err):
    app.logger.error('{url} {code} {name}'.format(
                     url=request.url, code=err.code, name=err.name))

    response = {
        'success': False,
        'message': err.description,
        'url': request.url
    }

    return jsonify(response), err.code

