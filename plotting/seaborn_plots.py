#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn.datasets


def load_data(cols=['CRIM', 'ZN', 'INDUS', 'CHAS', 'MEDV']):
    """
    Loads to Boston Housing Dataset
    """
    boston = sklearn.datasets.load_boston(return_X_y=False)
    df1 = pd.DataFrame(boston['data'], columns=boston['feature_names'])
    df2 = pd.DataFrame({'MEDV': boston['target']})
    df = pd.concat([df1, df2], axis=1)
    if cols is None:
        return df
    else:
        return df[cols]


def pair_plot(df, hue, filename=None):
    sns.set(style="whitegrid", rc={'figure.figsize': (12, 12)})
    sns_plot = sns.pairplot(df, hue=hue, size=2.5)
    if filename is not None:
        sns_plot.savefig(filename)


def heat_map(df, filename=None):
    sns_plot = sns.heatmap(df.corr())
    if filename is not None:
        fig = plt.gcf()
        fig.savefig(filename)


def main(args):
    df = load_data()
    print(df.head())
    if args.pairplot is True:
        pair_plot(df, 'CHAS', args.imgfile)
    if args.heatmap is True:
        heat_map(df, args.imgfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pairplot', action='store_true')
    parser.add_argument('--heatmap', action='store_true')
    parser.add_argument('--imgfile', default='seaborn_plot.png')
    args = parser.parse_args()
    main(args)

