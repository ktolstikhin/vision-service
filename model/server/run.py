#!/usr/bin/env python3
'''Start a model server.
'''
import time
import json
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from redis import StrictRedis

from utils import image, predictor
from utils.logger import init_logger


REDIS_HOST = 'redis'
IMAGE_QUEUE = 'images'
TOP_LABEL_NUM = 5


def get_args():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-b', '--batch-size', type=int, default=32,
                        help='image batch size')
    parser.add_argument('-s', '--sleep', type=float, default=0.05,
                        help='sleep secs between batch fetches')

    return parser.parse_args()


def main():
    args = get_args()
    logger = init_logger()
    redis = StrictRedis(REDIS_HOST)

    while True:
        imgs = redis.lrange(IMAGE_QUEUE, 0, args.batch_size - 1)

        if not imgs:
            time.sleep(args.sleep)
            continue

        redis.ltrim(IMAGE_QUEUE, len(imgs), -1)
        img_ids, img_list = [], []

        for img in imgs:
            img = json.loads(img.decode('utf-8'))
            img_dec = image.base64_decode(img['b64'])
            img_list.append(img_dec)
            img_ids.append(img['id'])
            logger.info(f'received image {img["id"]}')

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
            logger.info(f'store results for image {img_id}')


if __name__ == '__main__':
    main()

