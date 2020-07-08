#!/usr/bin/env python

import numpy as np
import pandas as pd

from typing import Dict


def fix_range(x_arr):
    new_x=[]
    for x in x_arr:
        if x < 0:
            new_x.append(x + 24)
        elif x > 23:
            new_x.append(x - 24)
        else:
            new_x.append(x)
    return np.array(new_x)


class TZTable():

    def __init__(self, d_time_zones: Dict):
        self._d_time_zones = d_time_zones

    def generate_series(self, label:str, time_zone: int):
        UTC = np.arange(24)
        return pd.Series(
            data=fix_range(UTC + time_zone),
            index=UTC,
            name=label
        )

    def generate_dataframe(self):
        df = pd.DataFrame()
        for label, time_zone in self._d_time_zones.items():
            df_s = pd.DataFrame(self.generate_series(label, time_zone))
            df = pd.concat((df, df_s), axis=1)
        df = df.reset_index()
        return df.rename(columns={'index': 'UTC'})

    def generate_excel(self, xl_file, verbose=True):
        df.to_excel(xl_file, index=False)
        if verbose:
            print(f'Created: {xl_file}')


if __name__ == "__main__":
    TZT = TZTable({
        'UTC-7': -7,
        'UTC+0': 0,
        'UTC+2': 2,
        'UTC+8': 8
    })
    df = TZT.generate_dataframe()
    print(df)
    TZT.generate_excel('TimeZones.xlsx')
