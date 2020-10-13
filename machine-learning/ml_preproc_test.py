#!/usr/bin/env python

import pandas as pd

from ml_preproc import ColSelector, RowVCSelector, RowRangeSelector


df = pd.DataFrame({
    'a': [0, 1, 2, 1, 0],
    'b': [0]*4 + [1],
    'c': [5]*5
})


def test_col_selector():
    CS1 = ColSelector(min_unique=1)
    X1 = CS1.fit_transform(df)
    assert X1.equals(df)

    CS2 = ColSelector(min_unique=2)
    X2 = CS2.fit_transform(df)
    assert X2.equals(df[['a', 'b']])

    CS3 = ColSelector(min_unique=3)
    X3 = CS3.fit_transform(df)
    assert X3.equals(df[['a']])


def test_row_vc_selector():
    RS1 = RowVCSelector(min_valuecount=1)
    X1 = RS1.fit_transform(df)
    assert X1.equals(df)

    RS2 = RowVCSelector(min_valuecount=2)
    X2 = RS2.fit_transform(df)
    assert X2.equals(df.loc[[0,1,3], :])


def test_row_range_selector():
    RRS1 = RowRangeSelector(column='a', min_value=1, max_value=1)
    X1 = RRS1.fit_transform(df)
    assert X1.equals(df.loc[[1,3],:])
