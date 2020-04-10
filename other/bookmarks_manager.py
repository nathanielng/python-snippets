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
from email.parser import BytesParser


# ----- Utilities Subroutines -----------------------------------------
def print_links(links):
    for i, link in enumerate(links):
        print(f'{i}: {link}')


# ----- HTML bookmarks file handling --------------------------------------------
def load_safari_bookmarks(filename):
    with open(filename) as f:
        html_txt = f.read()
    soup = BeautifulSoup(html_txt, 'html.parser')
    h3_list = [h3.text for h3 in soup.find_all('h3')]
    print(f"Categories: {', '.join(h3_list)}")
    df = links2df(links=soup.find_all('a'))
    print(df)
    return df


# ----- HTML file handling --------------------------------------------
def extract_links_from_html(filename):
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
        filename = os.path.expanduser(html_file)
        print(f'{i}. Loading {filename}', end='')
        links = extract_links_from_html(filename)
        links_df = links2df(links)
        print(f' (rows = {len(links_df)})')
        df = df.append(links_df)
    return df.drop_duplicates()


# ----- EML Handling --------------------------------------------------
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

    # m = re.findall(r'<a href="(.*?)".*>', txt)
    soup = BeautifulSoup(txt, 'html.parser')
    links = soup.find_all('a')
    if len(links) > 0:
        links2 = [link['href'] for link in links]
        urls = [link for link in links2 if (
            'http://flip.it' not in link and 'https://flipboard.com' not in link)]
        urls = [link for link in urls if (
            'http://zite.com' not in link and 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewSoftware?id=419752338&mt=8' not in link)]
    else:
        urls = re.findall(r'https?\://.*', txt)

    if len(urls) == 0:
        print(f'No URLs found in txt:\n{txt}')
        return []
    elif len(urls) == 1:
        return urls[0]
    else:
        return urls


def read_emlx(filename):
    """
    Reads a .emlx file and returns the title, body, message flags/plist
    See also: https://github.com/mikez/emlx
    """
    msg = emlx.read(filename)
    if 'Subject' in msg.headers:
        title = msg.headers['Subject']
    else:
        print(f'----- {filename} -----')
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


def read_eml(filename):
    """
    Reads a .eml file and returns the title, body, params, items
    """
    with open(filename, 'rb') as f:
        data = BytesParser().parse(f)
    body = data.get_payload()
    if isinstance(body, list):
        payload = ''
        for x in body:
            payload += x.get_payload()
        body = payload

    items = dict(data.items())
    title, _ = os.path.splitext(os.path.basename(filename))
    # title = items.get('Subject', '(no title)')
    msg_flags = data.get_params()
    # msg_date = items.get('Date', default='')
    # msg.plist
    return title, body, msg_flags, items


def load_email_folder(folder):
    """
    Loads a folder containing .eml or .emlx files
    and parses them for URLs
    """
    path = os.path.expanduser(folder)
    eml_files = glob.glob(f'{path}/*.eml')
    emlx_files = glob.glob(f'{path}/*.emlx')
    filenames = eml_files + emlx_files

    items = []
    for i, filename in enumerate(filenames):
        basename = os.path.basename(filename)
        print(f'{i}: {basename}')
        _, ext = os.path.splitext(basename)
        if ext == '.emlx':
            title, body, _, _ = read_emlx(filename)
        elif ext == '.eml':
            title, body, _, _ = read_eml(filename)
        items.append([title, body, basename])

    df = pd.DataFrame(items, columns=['Title', 'body', 'basename'])
    df['url'] = df['body'].apply(extract_links_from_txt)
    return df[['Title', 'url', 'body', 'basename']]


def main(args):
    df = pd.DataFrame()
    if args.html is not None:
        df = df.append(
            load_html_files(html_files=args.html.split(','))
        )
    if args.folder is not None:
        df = df.append(
            load_email_folder(folder=args.folder)
        )
        print(df.head(1).T)
    if args.safari_bookmarks is not None:
        df = df.append(
            load_safari_bookmarks(filename=args.safari_bookmarks)
        )

    df.to_csv(args.output, index=False)
    print(f"Created file: {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--html', default=None, help='Comma-separated list of html files containing bookmarks')
    parser.add_argument('--folder', default=None, help='Folder containing eml/emlx files')
    parser.add_argument('--safari_bookmarks', default=None, help='Safari-exported HTML bookmarks file')
    parser.add_argument('--output', default='bookmarks_manager.csv', help='Csv file for output dataframe')
    args = parser.parse_args()
    main(args)
