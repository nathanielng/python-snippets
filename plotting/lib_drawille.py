#!/usr/bin/env python
# -*- coding: ascii -*-

# Requirements:
# pip install drawilleplot

import numpy as np
import matplotlib
matplotlib.use('module://drawilleplot')
from matplotlib import pyplot as plt


def get_xy(n=101):
    x = np.linspace(0, 2*np.pi, n);
    y = np.sin(x)
    return x, y


def draw_plot(ax, x, y, label):
    ax.scatter(x, y, s=15, c="r", alpha=0.5, marker='x', label=label)
    ax.set_title('Plot')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.axis([x.min(), x.max(), y.min(), y.max()])
    ax.legend(loc='best')
    ax.annotate(label, xy=(np.pi/2.0, 0.5),
        horizontalalignment='center', verticalalignment='center', fontsize=12)


if __name__ == "__main__":
    x, y = get_xy()
    fig, ax = plt.subplots(1, 1, figsize=(5, 4))
    draw_plot(ax, x, y, label='sin(x)')
    plt.show()
