#!/usr/bin/env python


def dict2_to_tuplelist(d):
    """
    Converts a dictionary of dictionary items into a list of tuples
    """
    tuple_list = []
    data = []
    for k, v in d.items():
        for w, x in v.items():
            tuple_list.append((k, w))
            data.append(x)
    return tuple_list, data


def dict2_to_dataframe(d):
    """
    Converts a dictionary of dictionary items into a dataframe
    """
    tuple_list, data = dict_to_tuplelist(d)
    idx = pd.MultiIndex.from_tuples(tuple_list)
    return pd.DataFrame([data], columns=idx)


if __name__ == "__main__":
    pass

