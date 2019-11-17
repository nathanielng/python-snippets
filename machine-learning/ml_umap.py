#!/usr/bin/env python

import numpy as np
import pandas as pd
import umap

import dataset_gen as dg


if __name__ == "__main__":
    df, _ = dg.get_wine_dataset()
    print(df.head())
    X = df.iloc[:,:-1]

    um = umap.UMAP().fit_transform(X)
    print(um)

