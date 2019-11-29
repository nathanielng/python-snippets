#!/usr/bin/env python

import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import warnings


warnings.filterwarnings('ignore')

# ----- Kaggle Submission ---------------------------------------------
def submit_to_kaggle(model, X_test, sample_submission, submission_file='submission.csv'):
    submission = pd.read_csv(sample_submission, index_col=0)
    y_pred = model.predict(X_test)
    assert np.all(submission.index == X_test.index)
    submission.iloc[:, -1] = y_pred
    submission.to_csv(submission_file)


# ----- Kaggle Leaderboard --------------------------------------------
def extract_leaderboard_data(filename):
    df = pd.read_csv(filename)
    y, x = np.histogram(df['Score'], bins=50, density=True)
    yc = np.cumsum(y)
    y = y/np.max(y)
    yc = yc/np.max(yc)
    x_midpt = 0.5*(x[1:] + x[:-1])
    return df, x, y, yc, x_midpt


def plot_leaderboard_data(score, x_midpt, y, yc, outfile=None):
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.plot([score, score], [0, 1], color='black', label='Current Score')
    ax.bar(x_midpt, y, width=0.015, alpha=0.3, label='Histogram')
    ax.plot(x_midpt, yc, color='blue', label='Cumulative Histogram')
    ax.legend(loc='best', frameon=True)
    ax.set_ylabel('Count')
    ax.set_xlabel('Score')
    ax.grid(which='both', axis='both')
    plt.yscale('log')
    if outfile is not None:
        plt.savefig(outfile)
        print(f'{outfile} saved')


def extract_scores(filename, outfile='score.txt'):
    df = pd.read_csv(filename)
    df['Score'].to_csv(outfile, index=False, header=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--leaderboard', default=None)
    parser.add_argument('--score', default=None)
    parser.add_argument('--outfile', default='leaderboard.png')
    args = parser.parse_args()
    if args.leaderboard is not None and args.score is not None:
        df, x, y, yc, x_midpt = extract_leaderboard_data(args.leaderboard)
        plot_leaderboard_data(float(args.score), x_midpt, y, yc, args.outfile)
