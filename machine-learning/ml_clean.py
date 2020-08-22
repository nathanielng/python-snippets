#!/usr/bin/env python

import matplotlib.pyplot as plt
import pandas as pd

from typing import Dict


# ----- Find NAs -----
def find_NAs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return the count and fraction of NAs in a DataFrame
    """
    n = len(df)
    NAs = df.isna().sum()
    NAs = NAs[NAs > 0].sort_values(ascending=False)
    return pd.DataFrame({
        'Count': NAs.values,
        'Fraction': NAs.values / n
    }, index=NAs.index)


# ----- Duplicate Rows -----
def get_duplicated_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.duplicated(keep='first')]


def count_duplicated_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.duplicated(keep='first').sum()


def drop_duplicated_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df.duplicated(keep='first')]


# ----- One Hot Encoding -----
def create_dummies_fn(series: pd.Series,
                      new_columns: Dict[int, str]) -> pd.DataFrame:
    return pd.get_dummies(series).rename(
        columns=new_columns
    })


def replace_column_with_dummies(df: pd.DataFrame,
                                column_to_replace: str,
                                new_columns: Dict[int, str],
                                create_dummies_fn: Callable[..., pd.DataFrame]) -> pd.DataFrame:
    df_dummies=create_dummies_fn(df[column_to_replace], new_columns)
    return pd.concat(
        [df.drop(columns=[column_to_replace]), df_dummies],
        axis='columns'
    )


# ----- Value Counts -----
def count_uniques(df: pd.DataFrame, n: int):
    unique_cols = df.apply(pd.Series.nunique)
    unique_cols = unique_cols.index[unique_cols == n]
    return unique_cols


def valu_counts_df_n(df, n):
    u_cols = df.apply(pd.Series.nunique)
    u_cols = list(u_cols.index[u_cols == n])
    dd = {}
    for col in u_cols:
        x = []
        for k, v in dict(df[col].value_counts()).items():
            x = x + [int(k), v]
        dd[col] = x
    return pd.DataFrame(dd).T


def valu_counts_df(df, n_arr=[2, 3, 4, 5]):
    """
    Returns the value counts of each column in a DataFrame
    with column names in the index and (counts, values) as the columns
    """
    vc_df = pd.DataFrame()
    for n in n_arr:
        vc_df = vc_df.append(valu_counts_df_n(df, n))

    # Create column names
    cols = [x+1 for x in range(vc_df.shape[1]//2)]
    cols = [[f'c{x}', f'v{x}'] for x in cols]
    vc_df.columns = np.array(cols).flatten()
    return vc_df


def plot_value_counts1(df, column_name, image_h=1):
    df_data = df[column_name].value_counts().sort_values()
    _, ax = plt.subplots(1, 1, figsize=(8, image_h))
    df_data.plot.barh(title=column_name, ax=ax)
    for i, (_, data) in enumerate(df_data.iteritems()):
        ax.annotate(f'{data}', xy=(data+1, i-0.1), color='blue')
    ax.grid()


def plot_value_counts2(df, n_uniques=1, image_h=1):
    unique_cols = count_uniques(df, n=n_uniques)
    print(f"Columns with only {n_uniques} values: {','.join(unique_cols)}")
    for col in unique_cols:
        plot_value_counts1(df, col, image_h)


def plot_value_counts3(df, n_arr):
    unique_cols = {}
    for n in n_arr:
        unique_cols[n] = count_uniques(df, n)
    print(unique_cols)
    for n, cols in unique_cols.items():
        for col in cols:
            plot_value_counts2(df, col)


if __name__ == "__main__":
    pass
