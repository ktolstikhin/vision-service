#!/usr/bin/env python3
'''Start a model server.
'''
import time
import json
from argparse import ArgumentParser

from redis import StrictRedis

from utils import image, predictor
from utils.logger import init_logger


REDIS_HOST = 'redis'
IMAGE_QUEUE = 'images'
FETCH_SLEEP = 0.05
TOP_LABEL_NUM = 5


def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--batch-size', type=int,
                        default=32, help='image batch size')

    return parser.parse_args()


def main():
    args = get_args()
    logger = init_logger()
    redis = StrictRedis(REDIS_HOST)

    while True:
        imgs = redis.lrange(IMAGE_QUEUE, 0, args.batch_size - 1)

        if not imgs:
            time.sleep(FETCH_SLEEP)
            continue

        redis.ltrim(IMAGE_QUEUE, len(imgs), -1)
        img_ids, img_list = [], []

        for img in imgs:
            img = json.loads(img.decode('utf-8'))
            img_dec = image.base64_decode(img['b64'])
            img_list.append(img_dec)
            img_ids.append(img['id'])
            logger.info('received image {}'.format(img['id']))

        res_lists = predictor.predict(img_list, TOP_LABEL_NUM)

        for img_id, res_list in zip(img_ids, res_lists):
            results = {
                'predictions': [],
                'predicted_at': time.strftime('%Y%m%d_%H%M%S')
            }

            for _, label, proba in res_list:
                pred = {'label': label, 'proba': float(proba)}
                results['predictions'].append(pred)

            redis.set(img_id, json.dumps(results))
            logger.info('store results for image {}'.format(img_id))


if __name__ == '__main__':
    main()
