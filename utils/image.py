import base64
from io import BytesIO

from PIL import Image


def image_open(img_file):
    img_bytes = BytesIO(img_file)
    img = Image.open(img_bytes)

    return img.filename, img_bytes


def image_encode(img_bytes):
    data = img_bytes.getvalue()

    return base64.b64encode(data).decode('utf-8')


def image_decode(img_enc):
    enc_bytes = bytes(img_enc, encoding='utf-8')
    img_bytes = base64.decodestring(enc_bytes)
    img_bytes = BytesIO(img_bytes)

    return Image.open(img_bytes)

