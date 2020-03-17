#!/usr/bin/env python

# A tool for loading & saving parameters
# in a .json parameter file

import json


def load_json(filename):
    with open(filename, 'r') as f:
        d = json.load(f)
    return d


def save_json(d, filename):
    txt = json.dumps(x, ensure_ascii=True, indent=4)
    with open(filename, 'rw') as f:
        f.write(txt)
