#!/usr/bin/env python

"""
This is a module for generating datasets
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn.datasets


def anscombes_quartet():
    df = pd.read_fwf('data/anscombe.txt')  # np.loadtxt("anscombe.txt")
    return df


def load_sk_dataset(dataset_name: str):
    if dataset_name == 'boston':
        return sklearn.datasets.load_boston()
    elif dataset_name == 'breast_cancer':
        return sklearn.datasets.load_breast_cancer()
    elif dataset_name == 'diabetes':
        return sklearn.datasets.load_diabetes()
    elif dataset_name == 'digits':
        return sklearn.datasets.load_digits()
    elif dataset_name == 'iris':
        return sklearn.datasets.load_iris()
    elif dataset_name == 'linnerud':
        return sklearn.datasets.load_linnerud()
    elif dataset_name == 'wine':
        return sklearn.datasets.load_wine()
    else:
        return None


def plot_anscombe(data):
    fig = plt.figure(figsize=(10, 7))
    for i in range(4):
        i2 = i*2
        x = data.iloc[:, i2]
        y = data.iloc[:, i2+1]
        ax = fig.add_subplot(2, 2, i+1)
        ax.scatter(x, y)
        ax.plot(x, np.poly1d(np.polyfit(x, y, 1))(x), 'r')
        if (i == 0 or i == 2):
            ax.set_ylabel('y')
        if (i == 2 or i == 3):
            ax.set_xlabel('x')
    plt.savefig('anscombe.png')


aq = anscombes_quartet()
plot_anscombe(aq)
