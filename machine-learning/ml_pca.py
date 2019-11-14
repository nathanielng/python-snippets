#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.cluster import KMeans
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


def plot_kmeans_clusters(df, n, imgfile=None):
    kmeans = KMeans(n_clusters=n).fit(df)
    centroids = kmeans.cluster_centers_
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.scatter(df['pc1'], df['pc2'], c=kmeans.labels_.astype(float),
               marker='+', s=50, alpha=0.4)
    ax.scatter(x=centroids[:, 0], y=centroids[:, 1], c='red', s=100)
    if imgfile is not None:
        plt.savefig(imgfile)
