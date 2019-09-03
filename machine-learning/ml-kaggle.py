#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import warnings


warnings.filterwarnings('ignore')

def submit_to_kaggle(model, X_test, sample_submission, submission_file='submission.csv'):
    submission = pd.read_csv(sample_submission, index_col=0)
    y_pred = model.predict(X_test)
    assert np.all(submission.index == X_test.index)
    submission.iloc[:, -1] = y_pred
    submission.to_csv(submission_file)


def show_leaderboard(filename):
    df = pd.read_csv(filename)
    y, x = np.histogram(df['Score'], bins=50, density=True)
    yc = np.cumsum(y)
    y = y/np.max(y)
    yc = yc/np.max(yc)
    x_midpt = 0.5*(x[1:] + x[:-1])
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    ax.plot(x_midpt, y, label='y')
    ax.plot(x_midpt, yc, label='cumsum(y)')
    plt.savefig('leaderboard.png')


def extract_scores(filename, outfile='score.txt'):
    df = pd.read_csv(filename)
    df['Score'].to_csv(outfile, index=False, header=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--leaderboard', default=None)
    args = parser.parse_args()
    if args.leaderboard is not None:
        show_leaderboard(args.leaderboard)
