from flask import Flask, jsonify, abort, request

from .model import ModelClient


app = Flask(__name__)

app.config.from_object('server.config.default')
app.config.from_envvar('SERVER_APP_CONFIG', silent=True)

model_client = ModelClient('redis', app.logger)


@app.route('/')
@app.route('/api')
def index():
    return jsonify(success=True, message='send files to /api/predict')


@app.route('/api/predict')
def predict():
    timeout = app.config.get('PREDICTION_TIMEOUT')

    try:
        img_file = request.files['image']
        predictions = model_client.predict(img_file, timeout)
    except KeyError:
        app.logger.error('Failed to process request: No image found.')
        abort(400, description='no image found')
    except TimeoutError:
        app.logger.error('Failed to get predictions from the model server.')
        abort(500, description='model server does not respond')
    except:
        app.logger.exception('Unexpected error:')
        abort(500)

    return jsonify(success=True, message=predictions)


@app.errorhandler(400)
def bad_request(error):
    return jsonify(success=False, message=error.description), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify(success=False, message='resource not found'), 404


@app.errorhandler(500)
def server_error(error):
    msg = error.description or 'oops something went wrong'

    return jsonify(success=False, message=msg) , 500

