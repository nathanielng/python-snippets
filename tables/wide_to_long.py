#!/usr/bin/env python

# Converts tables between wide & long format
#
# For example:
#
#   Input Dataframe:
#          red  green  blue
#   Index                  
#   0.00   0.0    NaN   NaN
#   0.11   NaN    1.1   NaN
#   0.24   2.3    NaN   NaN
#   0.31   NaN    NaN   3.7
#   0.47   4.1    NaN   NaN
#   0.55   NaN    5.7   NaN
#   0.64   NaN    NaN   6.2
#   0.78   7.5    NaN   NaN
#   0.88   NaN    NaN   8.3
#
#   Output Dataframe:
#         Category  Value
#   Index                
#   0.00       red    0.0
#   0.24       red    2.3
#   0.47       red    4.1
#   0.78       red    7.5
#   0.11     green    1.1
#   0.55     green    5.7
#   0.31      blue    3.7
#   0.64      blue    6.2
#   0.88      blue    8.3
#

import argparse
import numpy as np
import pandas as pd


def get_sample_df():
    wide_df = pd.DataFrame({
        'red':   [0.0,    np.nan, 2.3,    np.nan, 4.1,    np.nan, np.nan, 7.5,    np.nan],
        'green': [np.nan, 1.1,    np.nan, np.nan, np.nan, 5.7,    np.nan, np.nan, np.nan],
        'blue':  [np.nan, np.nan, np.nan, 3.7,    np.nan, np.nan, 6.2,    np.nan, 8.3]
    }, index=[0.0, 0.11, 0.24, 0.31, 0.47, 0.55, 0.64, 0.78, 0.88])
    wide_df.index.name='Index'
    return wide_df


def wide_to_long(df_wide):
    df_long = df_wide.reset_index().melt(
        id_vars=['Index'],
        var_name='Category',
        value_name='Value').dropna(subset=['Value']).set_index('Index')
    return df_long


def wide_to_long2(df_wide):
    index_colname = df_wide.index.name
    df_stack = df_wide.stack().reset_index()
    df_stack.columns = [index_colname, 'Category', 'Value']
    df_stack.sort_values(['Category', index_colname], inplace=True)
    df_stack.set_index('Index', inplace=True)
    return df_stack


def demo():
    print('----- Original Wide Dataframe -----')
    df = get_sample_df()
    print(df)

    print('----- Wide to Long Using stack() -----')
    df_stack = wide_to_long2(df)
    print(df_stack)

    print('----- Wide to Long Using melt() with index dropped -----')
    df_long = df.melt(var_name='Category',
                      value_name='Value').dropna(subset=['Value'])
    print(df_long)

    print('----- Wide to Long Using melt() -----')
    df_long = wide_to_long(df)
    print(df_long)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', default='')
    parser.add_argument('--outfile', default='')
    args = parser.parse_args()

    if (args.infile == ''):
        demo()
    else:
        df_wide = pd.read_csv(args.infile, index_col=0)
        df_long = wide_to_long(df_wide)
        df_long.to_csv(args.outfile)
