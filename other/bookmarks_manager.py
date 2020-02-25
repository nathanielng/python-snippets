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
import emlx
import glob
import os
import pandas as pd
import re

from bs4 import BeautifulSoup


def print_links(links):
    for i, link in enumerate(links):
        print(f'{i}: {link}')


def extract_links_from_html(filename):
    with open(filename) as f:
        html_txt = f.read()
    soup = BeautifulSoup(html_txt, 'html.parser')
    links = soup.find_all('a')
    return links


def clean_txt(txt: str):
    txt = re.sub(r'=3D', r'=', txt)    # Replace '=3D' with '='
    txt = re.sub(r'=\r?\n', r'', txt)  # Replace '=\r?\n' with ''
    return txt


def extract_links_from_txt(txt: str):
    """
    Try to find links from text data in the forms:
    1. <a href = "..." ...>
    2. http://... or https://...
    """
    if not isinstance(txt, str):
        print(f'Expected string, but input txt={txt}')
        return []
    txt = clean_txt(txt)

    soup = BeautifulSoup(txt, 'html.parser')  # m = re.findall(r'<a href="(.*?)".*>', txt)
    links = soup.find_all('a')
    if len(links) > 0:
        urls = [link['href'] for link in links]
    else:
        urls = re.findall(r'https?\://.*', txt)
    
    if len(urls) == 1:
        return urls[0]
    else:
        return urls


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
        filename = os.path.expanduser(html_file)
        print(f'{i}. Loading {filename}', end='')
        links = extract_links_from_html(filename)
        links_df = links2df(links)
        print(f' (rows = {len(links_df)})')
        df = df.append(links_df)
    return df.drop_duplicates()


def read_emlx(filename):
    # See also: https://github.com/mikez/emlx
    msg = emlx.read(filename)
    if 'Subject' in msg.headers:
        title = msg.headers['Subject']
    else:
        title = '(no title)'
        print(f'Message.headers has no title: {msg.headers}')
        print(f'{msg.as_string()}')
    payload = msg.get_payload()
    if isinstance(payload, list):
        body = ''
        for x in payload:
            body += x.get_payload() + '\n'
    else:
        body = payload
    return title, body, msg.flags, msg.plist


def load_emlx_folder(emlx_folder):
    path = os.path.expanduser(emlx_folder)
    filenames = glob.glob(f'{path}/*.emlx')

    items = []
    for i, filename in enumerate(filenames):
        basename = os.path.basename(filename)
        print(f'{i}: {basename}')
        title, body, _, _ = read_emlx(filename)
        items.append([title, body])
    df = pd.DataFrame(items, columns=['Title', 'body'])
    df['url'] = df['body'].apply(extract_links_from_txt)
    return df[['Title', 'url', 'body']]


def main(args):
    df = pd.DataFrame()
    if args.html is not None:
        df = df.append(
            load_html_files(html_files=args.html.split(','))
        )
    if args.emlx is not None:
        df = df.append(
            load_emlx_folder(emlx_folder=args.emlx)
        )
        print(df.head(1).T)

    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', default=None, help='Comma-separated list of html files containing bookmarks')
    parser.add_argument('--emlx', default=None, help='Folder containing emlx files')
    parser.add_argument('--output', default='bookmarks_manager.csv', help='Csv file for output dataframe')
    args = parser.parse_args()
    main(args)
