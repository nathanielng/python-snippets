#!/usr/bin/env python

"""
This is a module for generating datasets
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn.datasets


def anscombes_quartet():
    df = pd.read_fwf('data/anscombe.txt')  # np.loadtxt("anscombe.txt")
    return df


def get_iris_dataset():
    from sklearn.datasets import load_iris
    iris = load_iris(return_X_y=False)
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target).replace(
        to_replace=[0, 1, 2], value=iris.target_names)
    y = pd.DataFrame({'target': y})
    df = pd.concat((X, y), axis=1)
    return df, iris.DESCR


def get_mnist_dataset():
    from sklearn.datasets import load_digits
    mnist = load_digits(n_class=10, return_X_y=False)
    X = pd.DataFrame(mnist.data)
    y = pd.DataFrame({'y': mnist.target})
    df = pd.concat((X, y), axis=1)
    return df, mnist.DESCR


def get_wine_dataset():
    from sklearn.datasets import load_wine

    wine = load_wine(return_X_y=False)
    X = pd.DataFrame(wine.data, columns=wine.feature_names)
    y = pd.Series(wine.target).replace(
        to_replace=[0, 1, 2], value=wine.target_names)
    y = pd.DataFrame({'class': y})
    df = pd.concat((X, y), axis=1)
    return df, wine.DESCR


def load_sk_dataset(dataset_name: str, return_X_y: bool):
    if dataset_name == 'boston':
        return sklearn.datasets.load_boston(return_X_y=return_X_y)
    elif dataset_name == 'breast_cancer':
        return sklearn.datasets.load_breast_cancer(return_X_y=return_X_y)
    elif dataset_name == 'diabetes':
        return sklearn.datasets.load_diabetes(return_X_y=return_X_y)
    elif dataset_name == 'digits':
        return sklearn.datasets.load_digits(return_X_y=return_X_y)
    elif dataset_name == 'iris':
        return sklearn.datasets.load_iris(return_X_y=return_X_y)
    elif dataset_name == 'linnerud':
        return sklearn.datasets.load_linnerud(return_X_y=return_X_y)
    elif dataset_name == 'wine':
        return sklearn.datasets.load_wine(return_X_y=return_X_y)
    else:
        return None


def load_sns_dataset(dataset_name: str):
    datasets = sns.get_dataset_names()
    if dataset_name not in datasets:
        return None
    return sns.load_dataset(dataset_name)


def gen_sk_dataset(dataset_name: str, **kwargs):
    if dataset_name == 'moons':
        X, y = sklearn.datasets.make_moons(**kwargs)
    else:
        X, y = sklearn.datasets.make_circles(**kwargs)

    df = pd.concat((pd.DataFrame(X), pd.DataFrame(y)), axis=1)
    df.columns=['x1', 'x2', 'y']
    return df


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


if __name__ == "__main__":
    aq = anscombes_quartet()
    plot_anscombe(aq)
