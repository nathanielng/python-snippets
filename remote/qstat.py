#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
import pandas as pd
import remote_host as rh

from io import StringIO
from remote_host import PBSHost, SSHHost
from IPython.display import display


pd.set_option('precision', 5)
pd.set_option('max_colwidth', 300)
pd.set_option('max_rows', 200)


def read_qstat(txt):
    separator_bars = txt.split('\n')[1]
    S = [ m.start() for m in re.finditer('([-]+)', separator_bars) ]
    S = np.array(S + [len(separator_bars)])
    widths = S[1:] - S[:-1]
    df = pd.read_fwf(StringIO(qstat_str), widths=widths)
    return df.iloc[1:, :]


PBS_USER = os.getenv('PBS_USER')
PBS_HOST = os.getenv('PBS_HOST')
PBS_KEY = os.getenv('PBS_KEY')

PBS = PBSHost(
    userid=PBS_USER,
    host=PBS_HOST,
    key=os.path.expanduser(PBS_KEY)
)
qstat = PBS.qstat()
PBS.close()


if __name__ == "__main__":
    pass
else:
    display(qstat)

