#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def get_dynamic_range1(df, axis=1):
    dr = df.apply(
        lambda x: pd.Series([x[x > 0].min(), x.max()]), axis=axis)
    dr['Dynamic Range'] = np.log10(dr[1] / dr[0])
    return dr


def get_dynamic_range2(df, axis=1):
    df_min = df.apply(lambda x: x[x > 0].min(), axis=axis)
    df_max = df.apply(lambda x: x.max(), axis=axis)
    dr = pd.concat((df_min, df_max), axis=1)
    dr['Dynamic Range'] = np.log10(dr[1] / dr[0])
    return dr


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


def plot_pca_evr(my_pca, style='bar', imgfile=None):
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    evr = np.cumsum(my_pca.explained_variance_ratio_)
    if style == 'bar':
        ax.bar(height=evr, x=np.arange(my_pca.n_components))
    elif style == 'line':
        ax.plot(evr)
    ax.set_xlabel('n')
    ax.set_ylabel('Variance')
    if imgfile is not None:
        plt.savefig(imgfile)


def plot_pca_scatter(df, label_list, labels, imgfile=None):
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.scatter(df['pc1'], df['pc2'], c=label_list,
               marker='o', s=50, alpha=1.0)
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')
    ax.grid()
    if imgfile is not None:
        plt.savefig(imgfile)


def plot_kmeans_clusters(df, n, imgfile=None):
    kmeans = KMeans(n_clusters=n).fit(df)
    centroids = kmeans.cluster_centers_
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.scatter(df['pc1'], df['pc2'], c=kmeans.labels_.astype(float),
               marker='+', s=50, alpha=0.4)
    ax.scatter(x=centroids[:, 0], y=centroids[:, 1], c='red', s=100)
    if imgfile is not None:
        plt.savefig(imgfile)
