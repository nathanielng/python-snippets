#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import pandas as pd


def display_correlations(df, imgfile=None, **kwargs):
    _, ax = plt.subplots(1, 1, **kwargs)
    ax.matshow(df.corr())
    if imgfile is not None:
        plt.savefig(imgfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv')
    parser.add_argument('--imgfile')
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    display_correlations(df, args.imgfile, figsize=(10, 10))
