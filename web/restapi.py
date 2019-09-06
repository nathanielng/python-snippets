#!/usr/bin/env python

import argparse
import json

from urllib.request import urlopen


def read_url(url):
    return urlopen(url).read().decode('utf-8')


def json_print(my_dict):
    jobj = json.loads(my_dict)
    print(json.dumps(jobj, indent=4))


def main(url):
    data = read_url(url)
    json_print(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    args = parser.parse_args()
    main(args.url)
