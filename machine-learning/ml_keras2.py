#!/usr/bin/env python

import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Dense, Dropout, Flatten, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator

n_GPUs = len(tf.config.experimental.list_physical_devices('GPU'))

print(f"Tensorflow version: {tf.__version__}")
print(f"Num GPUs Available: {n_GPUs}")


import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pathlib
import re


def load_dataset(img_path: str, verbose: bool = True):
    list_ds = tf.data.Dataset.list_files(img_path)
    return list_ds


def load(train_folder: pathlib.Path, test_folder: pathlib.Path):
    list_ds_train = load_dataset(str(train_folder/'*/*.jpg'))
    list_ds_test = load_dataset(str(test_folder/'*.jpg'))

    n_train = len(list(train_folder.glob('*/*.jpg')))
    class_names = np.array([
        item.name for item in train_folder.glob('*') if re.match('[0-9]{2}', item.name)
    ])
    return list_ds_train, list_ds_test, n_train, class_names


def train(folder):
    IMAGE_ROOT_FOLDER = pathlib.Path(folder)
    train_folder = pathlib.Path(IMAGE_ROOT_FOLDER/'train')
    test_folder = pathlib.Path(IMAGE_ROOT_FOLDER/'test')
    list_ds_train, list_ds_test, image_count, CLASS_NAMES = load(
        train_folder, test_folder)

    CLASS_CATEGORIES = len(CLASS_NAMES)
    print(f'No. of images: {image_count}')
    print(f'Class Names (total={CLASS_CATEGORIES}): {CLASS_NAMES.tolist()}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder')
    args = parser.parse_args()

    train(args.folder)

