#!/usr/bin/env python

# To download leaderboard data, use:
# kaggle competitions leaderboard --download [competition_name]

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import subprocess


def extract_leaderboard_data(df: pd.DataFrame, score_col: str = 'Score'):
    y, x = np.histogram(df[score_col], bins=50, density=True)
    yc = np.cumsum(y)
    y = y
    yc = yc
    x_midpt = 0.5*(x[1:] + x[:-1])
    return x, y, yc, x_midpt


def plot_leaderboard_data(x_midpt, y, yc, team_score, team_idx, total_teams, team_name, outfile=None):
    _, ax = plt.subplots(1, 1, figsize=(12, 5))

    ax.bar(x_midpt, y, width=0.012, label='Histogram', alpha=0.3)

    ax2 = ax.twinx()
    ax2.plot(x_midpt, yc, label='Cumulative Histogram', color='blue')
    ax2.set_ylabel('Cumulative')

    if isinstance(team_score, float):
        ax.axvline(x=team_score, ls='--',
                   color='purple', label='Current Score')
        txt = f' {team_name}: Score = {team_score:.4f} ({team_idx} of {total_teams})'
        ax.annotate(txt, xy=(team_score, 0), rotation=90, ha='right', va='bottom')
    ax.legend(loc='best', frameon=True)
    ax.set_ylabel('Count')
    ax.set_xlabel('Score')
    ax.grid(which='both', axis='both')
    ax.set_title('Leaderboard')
    if outfile is not None:
        plt.savefig(outfile)
        print(f"Saved {outfile}")


def download_data(competition: str):
    csv_file = f'{competition}.zip'
    if not os.path.isfile(csv_file):
        cmd_line = f'kaggle competitions leaderboard --download {competition}'
        print(cmd_line)
        r = subprocess.call(cmd_line.split())
        print(r)

    df = pd.read_csv(f'{competition}.zip', index_col=0)
    return df


def team_stats(df: pd.DataFrame, team_name: str, pad: int = 5):
    df = df.sort_values(by='Score', ascending=False).reset_index()
    df_team = df[df['TeamName'] == team_name]
    team_idx = df_team.index[0]
    print(df.iloc[team_idx-pad:team_idx+pad+1, :])

    team_score = df_team['Score'].iloc[0]
    print(f'Team Score: {team_score}')
    print(f'Team Rank: {team_idx} of {len(df)}')    
    return team_score, team_idx, len(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--competition', type=str, help='Name of competition')
    parser.add_argument('--team', type=str, default='', help='Name of your team')
    parser.add_argument('--imgfile', type=str, default='leaderboard.pdf', help='Name of output image')
    args = parser.parse_args()

    df = download_data(args.competition)
    if args.team == '':
        print(df.head())
    else:
        team_score, team_idx, team_total = team_stats(df, team_name=args.team)

        x, y, yc, x_midpt = extract_leaderboard_data(df)
        plot_leaderboard_data(x_midpt, y, yc, team_score, team_idx,
                              team_total, args.team, args.imgfile)
