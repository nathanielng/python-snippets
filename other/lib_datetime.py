#!/usr/bin/env python

import datetime


def get_datestamp(dt=datetime.datetime.now(), fmt='%Y%m%d'):
    """
    Returns a date stamp.
    Default format: YYYYMMDD
    """
    return dt.strftime(fmt)

def get_datetimestamp(dt=datetime.datetime.now(), fmt='%Y%m%d-%H%Mh'):
    """
    Returns a date-time stamp.
    Default format: YYYYMMDD-HHMMh
    """
    return dt.strftime(fmt)


if __name__ == "__main__":
    print(f'Date Stamp: {get_datestamp()}')
    print(f'Date-Time Stamp: {get_datetimestamp()}')
