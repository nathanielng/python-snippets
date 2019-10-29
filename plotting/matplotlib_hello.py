#!/usr/env/bin python
# -*- coding: ascii -*-

import numpy as np
import matplotlib.pyplot as plt


def makefig():
    fig = plt.figure("My Plots",facecolor='white')
    ax = fig.add_subplot(211, frame_on=True)
    ax.set_title(r'$y = \exp(-x/\pi) \cos(4x)$')
    ax.set_ylabel('$y$')
    ax.plot([1, 3, 5, 7], [0.5, 2.1, 0.95, 0.7], 'ro-', lw=2)
    ax.axis([0, 8, 0, 2.5])
    plt.grid(True)
  
    ax1= fig.add_subplot(212, frame_on=True)
    x = np.arange(0, 2.0, 0.05)
    y = np.sin(x*np.pi)
    ax1.set_xlabel('$x$', fontsize=12, color='red')
    ax1.set_ylabel('$y$', fontsize=12, color='red')
    ax1.plot(x, y)
    plt.xlim( 0,2)
    plt.ylim(-1,1)
    plt.grid(True)
    plt.text(1.0,0.1, r'$y=\sin(\pi x)$', fontsize=12, color='blue')

    fig.savefig("matplotlib_hello.png")


if __name__ == "__main__":
    makefig()

