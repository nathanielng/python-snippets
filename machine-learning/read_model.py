#!/usr/bin/env python

import argparse
import pickle


def read_pickle_file(filename):
    with open('model.pkl', 'rb') as f:
        data = pickle.load(f)
    return data


def main(args):
    read_pickle_file(args.file)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    args = parser.parse_args()
    main(args)