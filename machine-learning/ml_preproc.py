#!/usr/bin/env python

import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


def get_small_nonzeros(df, cutoff):
    """
    Retrieves the small, non-zero values in a dataframe
    """
    m1 = df.values > 0
    m2 = df.values < cutoff
    small_values = pd.DataFrame(
        np.argwhere(m1 & m2), columns=['i', 'j'], dtype=int)
    small_values['value'] = 0
    small_values['row_index'] = 0
    small_values['col_index'] = 0
    for idx, data in small_values.iterrows():
        i = int(data[0])
        j = int(data[1])
        small_values.loc[idx, 'value'] = df.iloc[i, j]
        small_values.loc[idx, 'row_index'] = df.index[i]
        small_values.loc[idx, 'col_index'] = df.columns[j]
    return small_values


def get_dynamic_range(df, axis=1):
    df_min = df.apply(lambda x: x[x > 0].min(), axis=axis)
    df_max = df.apply(lambda x: x.max(), axis=axis)
    dr = pd.concat((df_min, df_max), axis=1)
    dr['Dynamic Range'] = np.log10(dr[1] / dr[0])
    return dr.rename(columns={0: 'Min', 1: 'Max'})


def remove_columns(df, min_unique):
    unique_cols = df.apply(pd.Series.nunique)
    cols_to_keep = unique_cols.index[unique_cols >= min_unique]
    return df[cols_to_keep]


def identify_rows_to_drop(df, col, cutoff):
    vc = df[col].value_counts()
    rows = vc[vc < cutoff].index
    return list(df[df[col].isin(rows)].index)


class ColSelector(BaseEstimator, TransformerMixin):
    """
    Select only columns with a minimum number of unique values
    """

    def __init__(self, min_unique=2):
        self._cols_to_keep = None
        self._min_unique = min_unique

    def get_params(self, deep=True):
        return {'min_unique': self._min_unique}

    def set_params(self, **params):
        self._min_unique = params['min_unique']

    def fit(self, X: pd.DataFrame, y=None):
        unique_cols = X.apply(pd.Series.nunique)
        self._cols_to_keep = unique_cols.index[unique_cols >= self._min_unique]
        return self

    def transform(self, X, y=None):
        return X[self._cols_to_keep].copy()


class ColRemover(BaseEstimator, TransformerMixin):
    """
    Removes from a dataframe, the columns that you specify
    """

    def __init__(self, columns_to_remove):
        self._columns_to_remove = columns_to_remove
        self._columns_to_keep = None

    def get_params(self, deep=True):
        return {'columns_to_remove': self._columns_to_remove}

    def set_params(self, **params):
        self._columns_to_remove = params['columns_to_remove']

    def fit(self, X: pd.DataFrame, y=None):
        self._columns_to_keep = [
            x for x in X.columns if x not in self._columns_to_remove
        ]
        return self

    def transform(self, X, y=None):
        return X[self._columns_to_keep].copy()


class RowVCSelector(BaseEstimator, TransformerMixin):
    """
    Drops rows if the valuecount for the value in that row
    is lower than the minimum valuecount. Do this for all
    columns.
    """

    def __init__(self, min_valuecount=2):
        self._rows_to_drop = None
        self._rows_to_keep = None
        self._min_valuecount = min_valuecount

    def get_params(self, deep=True):
        return {'min_valuecount': self._min_valuecount}

    def set_params(self, **params):
        self._min_valuecount = params['min_valuecount']

    def fit(self, X: pd.DataFrame, y=None):
        rows_to_drop = []
        for col in X.columns:
            rows_to_drop = rows_to_drop + \
                identify_rows_to_drop(X, col, cutoff=self._min_valuecount)
        self._rows_to_drop = rows_to_drop
        self._rows_to_keep = [r for r in X.index if r not in rows_to_drop]
        return self

    def transform(self, X, y=None):
        return X.loc[self._rows_to_keep, :].copy()


class RowRangeSelector(BaseEstimator, TransformerMixin):
    """
    Drops rows where if the value in that column is
    outside a specified range
    """

    def __init__(self, column, min_value, max_value):
        self._column = column
        self._min_value = min_value
        self._max_value = max_value
        self._rows_to_keep = None

    def get_params(self, deep=True):
        return {
            'column': self._column,
            'min_value': self._min_value,
            'max_value': self._max_value
        }

    def set_params(self, **params):
        self._column = params['column']
        self._min_value = params['min_value']
        self._max_value = params['max_value']

    def fit(self, X: pd.DataFrame, y=None):
        m1 = X[self._column] >= self._min_value
        m2 = X[self._column] <= self._max_value
        self._rows_to_keep = (m1 & m2)
        return self

    def transform(self, X, y=None):
        return X.loc[self._rows_to_keep, :].copy()
