#!/usr/bin/env python

"""
This script reads server information from ~/.ssh_config
"""

import json
import os
import paramiko


def parse_ssh_config():
    filename = os.path.expanduser('~/.ssh/config')
    sc = paramiko.SSHConfig()
    with open(filename) as f:
        sc.parse(f)
    return sc


if __name__ == "__main__":
    sc = parse_ssh_config()
    print(json.dumps(sc.__dict__, indent=4))
