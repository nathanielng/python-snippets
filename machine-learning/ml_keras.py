#!/usr/bin/env python

import numpy as np
import pathlib
import re
import tensorflow as tf


class tfDataset():

    def __init__(self, img_path: pathlib.Path):
        """
        Loads images from a path in the form:
        path/{category}/*.jpg
        """
        self._img_path = img_path
        self._dataset = tf.data.Dataset.list_files(
            str(img_path/'*/*.jpg')
        )

    def image_count(self):
        return len(list(
            self._img_path.glob('*/*.jpg')
        ))

    def class_names(self, dir_pattern='.*'):
        class_names = [
            c.name for c in self._img_path.glob('*')
            if re.match(dir_pattern, c.name)
        ]
        return np.array(class_names)


if __name__ == "__main__":
    pass
