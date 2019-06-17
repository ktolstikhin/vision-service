import json
import time
import uuid
import base64
import logging
from io import BytesIO

from PIL import Image
from redis import StrictRedis


class ModelClient(object):

    IMAGE_QUEUE = 'vision-service-images'
    FETCH_SLEEP = 0.05

    def __init__(self, redis_host, logger=None):
        self.redis = StrictRedis(redis_host)
        self.logger = logger or logging.getLogger()

    def predict(self, img_file, timeout=None):
        img_bytes = BytesIO(img_file)
        img = Image.open(img_bytes)

        self.logger.info(
            'Process image file {n} {s}'.format(n=img.filename, s=img.size))

        data = img_bytes.getvalue()
        img_b64 = base64.b64encode(data).decode('utf-8')
        img_id = uuid.uuid4().hex

        queue_data = json.dumps({'img_id': img_id, 'img_b64': img_b64})
        self.redis.rpush(self.IMAGE_QUEUE, queue_data)

        t_start = time.time()

        while True:
            redis_data = self.redis.get(img_id)

            if redis_data is not None:
                redis_data = redis_data.decode('utf-8')
                predictions = json.loads(redis_data)
                self.redis.delete(img_id)
                break

            if timeout and time.time() - t_start > timeout:
                raise TimeoutError

            time.sleep(self.FETCH_SLEEP)

        self.logger.info('{n} done'.format(n=img.filename))

        return predictions

