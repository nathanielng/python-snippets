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


def extract_skip(x, y, skip):
    return x.values[::skip], y.values[::skip]


def interpolate_xy_lagrange(x, y):
    new_x = create_x_for_interpolation(x.values)
    fn = lagrange(x.values[::skip], y.values[::skip])
    return new_x, fn(new_x)


def interpolate_xy_interp1d(x, y):
    new_x = create_x_for_interpolation(x.values[::skip])
    fn = interp1d(x.values[::skip], y.values[::skip], kind=kind)
    return new_x, fn(new_x)


def interpolate_xy_lowess(x, y, frac):
    new_x = create_x_for_interpolation(x.values)
    new_xy = sm.nonparametric.lowess(y, x, frac=frac)
    return new_xy[:, 0], new_xy[:, 1]


def interpolate_xy_kernelreg(x, y):
    new_x = create_x_for_interpolation(x.values)
    kr = KernelReg(y, x, 'c')
    new_y, _ = kr.fit(new_x)
    return new_x, new_y


if __name__ == "__main__":
    pass
