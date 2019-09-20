#!/usr/bin/env python

import argparse
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use('agg')
import matplotlib.pyplot as plt


def plot_xy(x, y, imgfile=None, figsize=(7, 5)):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.plot(x, y)
    if imgfile is not None:
        fig.savefig(imgfile, figsize=figsize)


def create_sample(noise=0.05, n_pts=50, filename=None):
    x = np.linspace(0, 2, n_pts)
    y = np.sin(np.pi * x) + noise * np.random.uniform(0, 1, n_pts)
    df = pd.DataFrame({ 'x': x, 'y': y })
    if filename is not None:
        df.to_csv(filename, index=False)
    return df


def main(args):
    df = create_sample(filename=args.samplefile)
    plot_xy(df.x, df.y, args.imgfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--imgfile', help='Output image')
    parser.add_argument('--samplefile', help='Sample datafile')
    args = parser.parse_args()
    main(args)
