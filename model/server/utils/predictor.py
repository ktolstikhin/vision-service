import numpy as np
from keras.applications import imagenet_utils
from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.preprocessing.image import img_to_array


model = ResNet50()
IMAGE_SIZE = (224, 224)


def preprocess_images(img_list):
    arr_list = []

    for img in img_list:

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img = img.resize(IMAGE_SIZE)
        img_arr = img_to_array(img)
        arr_list.append(img_arr)

    inputs = np.array(arr_list)

    return preprocess_input(inputs)


def predict(img_list):
    inputs = preprocess_images(img_list)
    classes = model.predict(inputs)

    return imagenet_utils.decode_predictions(classes)

