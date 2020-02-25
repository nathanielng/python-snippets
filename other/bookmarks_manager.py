#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Bookmark Manager
#
# Tasks Performed:
# 1. Extract links from a html file using Beautiful Soup
#    with search pattern <a href=...>Title</a>
#    into a Pandas Dataframe
# 2. Removes duplicate entries
#

import argparse
import os
import pandas as pd

from bs4 import BeautifulSoup


def print_links(links):
    for i, link in enumerate(links):
        print(f'{i}: {link}')


def extract_links(filename):
    with open(filename) as f:
        html_txt = f.read()
    soup = BeautifulSoup(html_txt, 'html.parser')
    links = soup.find_all('a')
    return links


def links2df(links):
    rows = []
    for link in links:
        try:
            title = link.text
            url = link['href']
        except:
            print('... skipping')
            print(f'Link = {link}')
            continue

        row = {
            'Title': link.text,
            'url': link['href']
        }
        rows.append(row)
    return pd.DataFrame(rows)


def load_html_files(html_files):
    df = pd.DataFrame()
    for i, html_file in enumerate(html_files):
        print(f'{i}. Loading {html_file}', end='')
        links = extract_links(html_file)
        links_df = links2df(links)
        print(f' (rows = {len(links_df)})')
        df = df.append(links_df)
    return df.drop_duplicates()


def main(args):
    df = load_html_files(html_files=args.html.split(','))
    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', help='Comma-separated list of html files containing bookmarks')
    parser.add_argument('--output', default='bookmarks_manager.csv', help='Csv file for output dataframe')
    args = parser.parse_args()
    main(args)
