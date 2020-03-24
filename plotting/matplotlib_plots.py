#!/usr/bin/env python

import argparse
import io
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use('agg')
import matplotlib.pyplot as plt

from matplotlib.ticker import FormatStrFormatter, MultipleLocator
from pandas.plotting import scatter_matrix


def area_under_curve(x, y):
    n = x.shape[0]
    area = np.trapz(y[:(n-1)//2+1], dx=x[1]).item()
    return area


def plot_xy(x, y, imgfile=None, figsize=(7, 5)):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.plot(x, y)
    if imgfile is not None:
        fig.savefig(imgfile, figsize=figsize)


def plot_xy2(x, y, title, label, imgfile=None, figsize=(10, 7)):
    fig = plt.figure(num=1, figsize=figsize, dpi=100,
                     facecolor='w', edgecolor='k')
    ax  = fig.add_subplot(111)
    plt.grid(True)
    plt.title(title,fontsize=16)
    plt.xlabel('$x$',fontsize=16,color='black')
    plt.ylabel('$y$',fontsize=16,color='black')
    plt.xlim(x.min(),x.max())
    plt.ylim(y.min(),y.max())
    lines = plt.plot(x, y, c='g', marker='o', lw=2, linestyle='--', label=label)

    area = area_under_curve(x,y)
    plt.annotate(r"Area $\approx$ %.4f / $\pi$" % (area*np.pi),xy=(0.3,0.2), fontsize=14, color='white')
    ax.fill_between(x, y, 0.0, where=y>0.0, interpolate=True,
        facecolor='pink', alpha=0.5)

    plt.legend(loc=1,fontsize=14)
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.yaxis.set_major_locator(MultipleLocator(0.25))
    ax.yaxis.set_minor_locator(MultipleLocator(0.05))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.xaxis.set_minor_locator(MultipleLocator(0.1))
    if imgfile is not None:
        plt.savefig(imgfile, figsize=figsize, dpi=300)


def plot_xyz(X, Y, Z, style=1, imgfile=None, figsize=(7,5)):
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    if style == 1:
        ax.scatter(X,Y,c=Z,marker='x',s=100)
    else:
        ax.scatter(X, Y, c=Z, s = 2000*(Z**2),
            facecolors='none', edgecolors='face')

    if imgfile is not None:
        fig.savefig(imgfile, figsize=figsize)


def create_sample_from_text(text_data="1.0 2.0 0.3\n2.0 4.0 0.5"):
    data = np.loadtxt(io.StringIO(text_data))
    X = data[:,0]
    Y = data[:,1]
    Z = data[:,2]
    return X, Y, Z


def create_sample(noise=0.05, n_pts=100, filename=None):
    x = np.linspace(0, 2, n_pts)
    y = np.sin(np.pi * x) + noise * np.random.uniform(0, 1, n_pts)
    z = np.cos(np.pi * x)
    df = pd.DataFrame({ 'x': x, 'y': y, 'z': z })
    if filename is not None:
        df.to_csv(filename, index=False)
    return df


def main(args):
    df = create_sample(filename=args.samplefile)
    if args.mode == '2d':
        plot_xy2(df.x, df.y, title='2D Plot', label='sin(x) + noise', imgfile=args.imgfile)
    else:
        plot_xyz(df.x, df.y, df.z, imgfile=args.imgfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--imgfile', default='sample.png', help='Output image')
    parser.add_argument('--samplefile', default=None, help='Sample datafile')
    parser.add_argument('--mode', default='2d', help='2d or 3d')
    args = parser.parse_args()
    main(args)
