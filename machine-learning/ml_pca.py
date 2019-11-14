#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def do_pca(df, n, scale=True):
    pca_cols = ('pc' + pd.Series(np.arange(n)+1).astype(str)).values
    if scale is True:
        X = StandardScaler().fit_transform(df.values)
    else:
        X = df.values
    my_pca = PCA(n_components=n)
    my_pcomp = my_pca.fit(X)
    my_df = pd.DataFrame(data = my_pca.fit_transform(X), columns = pca_cols)
    return my_df, my_pca


def plot_pca(my_pca, style='bar'):
    evr = np.cumsum(my_pca.explained_variance_ratio_)
    if style == 'bar':
        plt.bar(height=evr, x=np.arange(my_pca.n_components))
    elif style == 'line':
        plt.plot(evr)
    plt.xlabel('n')
    plt.ylabel('Variance')
