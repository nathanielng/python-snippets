#!/usr/bin/env python

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

