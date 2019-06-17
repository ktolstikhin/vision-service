import base64
from io import BytesIO

from PIL import Image


def base64_decode(img_b64):
    enc_bytes = bytes(img_b64, encoding='utf-8')
    img_bytes = base64.decodestring(enc_bytes)
    img_bytes = BytesIO(img_bytes)

    return Image.open(img_bytes)

