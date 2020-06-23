#!/usr/bin/env python

import pathlib
import tensorflow as tf:


def load_dataset(img_path: pathlib.Path):
    """
    Loads images from a path in the form:
      path/{category}/*.jpg
    """
    return tf.data.Dataset.list_files(
        str(img_path/'*/*.jpg')
    )


if __name__ == "__main__":
    pass
