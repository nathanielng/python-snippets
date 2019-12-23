#!/usr/bin/env python

import argparse
import glob
import matplotlib.image
import numpy as np


def img2array(imgfile):
    """
    Converts an image file into a 2D numpy array
    """
    return matplotlib.image.imread(imgfile)


def load_images(input_files):
    """
    Flattens each image in a folder into a 1D numpy array.
    Next, each 1D numpy array is stacked into a 2D numpy array,
    where each row of the image is the flattened version of the image
    """
    imgfiles = glob.glob(input_files)
    arr = []
    for i, imgfile in enumerate(imgfiles):
        arr.append(img2array(imgfile).reshape(-1,1))
    return np.hstack(arr).T


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='*.png')
    args = parser.parse_args()
    load_images(args.input)
