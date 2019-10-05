import argparse
import autosklearn.regression
import os
import pandas as pd
import sklearn.model_selection
import sklearn.metrics


def main(args):
    df = pd.read_csv(os.path.abspath(args.file))
    print(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    args = parser.parse_args()
    main(args)

