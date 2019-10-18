#!/usr/bin/env python

import numpy as np
import pandas as pd
import seaborn as sns
import sklearn.datasets


def load_data():
    """
    Loads to Boston Housing Dataset
    """
    boston = sklearn.datasets.load_boston(return_X_y=False)
    df1 = pd.DataFrame(boston['data'], columns=boston['feature_names'])
    df2 = pd.DataFrame({'MEDV': boston['target']})
    df = pd.concat([df1, df2], axis=1)
    return df


def pair_plot(df):
    sns.set(style="whitegrid", rc={'figure.figsize': (12, 12)})
    sns.pairplot(df, hue='CHAS', size=2.5)


def heat_map(df):
    sns.heatmap(df.corr())


if __name__ == "__main__":
    df = load_data()
    print(df.head())
