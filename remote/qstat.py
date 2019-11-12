#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
import remote_host as rh

from remote_host import PBSHost, SSHHost
from IPython.display import display

pd.set_option('precision', 5)
pd.set_option('max_colwidth', 300)
pd.set_option('max_rows', 200)

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

