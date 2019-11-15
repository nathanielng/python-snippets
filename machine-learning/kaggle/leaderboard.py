import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys


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
    ax.bar(x_midpt, y, width=0.015, label='Histogram', alpha=0.3)
    ax.plot(x_midpt, yc, label='Cumulative Histogram', color='blue')
    ax.legend(loc='best', frameon=True)
    ax.set_ylabel('Count')
    ax.set_xlabel('Score')
    ax.grid(which='both', axis='both')
    plt.yscale('log')
    if outfile is not None:
        plt.savefig(outfile)
        print(f"Saved {outfile}")


if __name__ == "__main__":
    filename = sys.argv[1]
    score = float(sys.argv[2])
    imgfile = sys.argv[3]
    if imgfile != '':
        df, x, y, yc, x_midpt = extract_leaderboard_data(filename)
        plot_leaderboard_data(score, x_midpt, y, yc, imgfile)
