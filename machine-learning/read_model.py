#!/usr/bin/env python

import argparse
import pickle

from azureml.train import automl


def read_pickle_file(filename):
    with open(filename, 'rb') as f:
        model = pickle.load(f)
    return model


def main(args):
    model = read_pickle_file(args.file)
    print(model)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    args = parser.parse_args()
    main(args)

