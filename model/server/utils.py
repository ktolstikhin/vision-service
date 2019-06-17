import base64
from io import BytesIO

from PIL import Image


def base64_decode_image(img_enc):
    enc_bytes = bytes(img_enc, encoding='utf-8')
    img_bytes = base64.decodestring(enc_bytes)
    img_bytes = BytesIO(img_bytes)

    return Image.open(img_bytes)

