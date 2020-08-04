#!/usr/bin/env python

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


if __name__ == "__main__":
    pass
