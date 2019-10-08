import json
import time
import uuid
import base64
from io import BytesIO

from PIL import Image
from redis import StrictRedis


class ModelClient(object):

    IMAGE_QUEUE = 'images'
    FETCH_SLEEP = 0.01

    def __init__(self, redis_host):
        self.redis = StrictRedis(redis_host)

    def predict(self, img_file, timeout=None):
        img = Image.open(img_file)

        img_bytes = BytesIO()
        img.save(img_bytes, img.format)
        data = img_bytes.getvalue()

        img_b64 = base64.b64encode(data).decode('utf-8')
        img_id = uuid.uuid4().hex

        queue_data = json.dumps({'id': img_id, 'b64': img_b64})
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

        return predictions

