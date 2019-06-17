#!/usr/bin/env python3
'''Start a model server.
'''
import time
import json
from argparse import ArgumentParser

from redis import StrictRedis

from utils import image, predictor


REDIS_HOST = 'redis'
IMAGE_QUEUE = 'images'
FETCH_SLEEP = 0.05


def get_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-b', '--batch-size', type=int,
                        default=32, help='image batch size')

    return parser.parse_args()


def main():
    args = get_args()
    redis = StrictRedis(REDIS_HOST)

    while True:
        imgs = redis.lrange(IMAGE_QUEUE, 0, args.batch_size - 1)
        img_ids, img_list = [], []

        for img in imgs:
            img = json.loads(img.decode('utf-8'))
            img_pil = image.base64_decode(img['b64'])
            img_list.append(img_pil)
            img_ids.append(img['id'])

        if not img_ids:
            time.sleep(FETCH_SLEEP)
            continue

        res_lists = predictor.predict(img_list)

        for img_id, res_list in zip(img_ids, res_lists):
            predictions = []

            for _, label, proba in res_list:
                pred = {
                    'label': label,
                    'proba': float(proba),
                    'predicted_at': time.strftime('%Y%m%d_%H%M%S')
                }
                predictions.append(pred)

            redis.set(img_id, json.dumps(predictions))

        redis.ltrim(IMAGE_QUEUE, len(img_ids), -1)


if __name__ == '__main__':
    main()

