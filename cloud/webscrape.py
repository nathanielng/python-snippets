#!/usr/bin/env python

import argparse
import selenium

from selenium import webdriver


# ----- Open Browser -----
try:
    browser = webdriver.Safari()
except Exception as e:
    print("Could not open Safari browser")
    print(f"Exception: {e}")
    quit()


def main(args):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--xpath')
    args = parser.parse_args()
    main(args)
 
