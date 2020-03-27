#!/usr/bin/env python

import json
import pandas as pd


PARAMETER_FILE = "params.json"


def load_params(filename):
    with open(filename, 'r') as f:
        params = json.load(f)
    return params


def extract_xy(df, columns, logx=False, logy=False):
    x_col = columns['x_col']
    y_col = columns['y_col']

    if logx is True:
        x = np.log(df.loc[:, x_col])
    else:
        x = df.loc[:, x_col]

    if logy is True:
        y = np.log(df.loc[:, y_col])
    else:
        y = df.loc[:, y_col]
    return x, y


def extract_xy_tag(df, tag, columns):
    category_col = columns['category_col']
    df_slice = df.loc[df[category_col] == tag]
    x, y = extract_xy(df_slice, columns, logx=logx, logy=logy)
    return x, y


def create_x_for_interpolation(x):
    """
    Creates equally spaced points from x.min() to x.max(),
    rounded to the nearest integer
    """
    min_x = np.ceil(x.min())
    max_x = np.floor(x.max())
    x_range = max_x - min_x
    return min_x + np.arange(x_range+1)


if __name__ == "__main__":
    pass
