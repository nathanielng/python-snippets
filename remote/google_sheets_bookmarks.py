#!/usr/bin/env python

# Description:
# 1. Retrieves a URL from the clipboard
# 2. Fetches the web page for the URL
# 3. Extracts title from the web page
# 4. Appends [category, title, url] to a Google Drive Spreadsheet

import argparse
import json
import os
import re
import requests
import sys

from bs4 import BeautifulSoup
from google_sheets import GoogleSpreadsheet
from pandas.io.clipboard import clipboard_get


HOME = os.getenv('HOME')

# ----- Load Parameters -----
with open('google_sheets_bookmarks.json') as f:
    params = json.load(f)

GDRIVE_CREDENTIALS = os.getenv('GDRIVE_CREDENTIALS', None)
GDRIVE_SPREADSHEET = params['GDRIVE_SPREADSHEET']
BOOKMARKS_SPREADSHEET_ID = params['BOOKMARKS_SPREADSHEET_ID']
RESEARCH_TOOLS = os.path.expanduser(params["RESEARCH_TOOLS_PATH"])
sys.path.append(RESEARCH_TOOLS)
import webloc2csv


# ----- Subroutines -----
def open_spreadsheet():
    try:
        GS = GoogleSpreadsheet(GDRIVE_CREDENTIALS, GDRIVE_SPREADSHEET, None)
    except Exception as e:
        print(f'Exception: {e}')
        print(f'Could not open spreadsheet: {GDRIVE_SPREADSHEET}')
        return
    worksheets = GS.get_worksheets()
    print(f"Worksheets: {','.join(worksheets)}")
    return GS


def upload_bookmark(GS, title, url):
    title = webloc2csv.sanitize_title(title)
    title = re.sub('\n', ' • ', title)  # Additional sanitization

    tags1 = webloc2csv.get_keyword_tags(title)
    tags2 = webloc2csv.get_url_tags(url)
    tags = (tags1 + ' ' + tags2).strip()
    tags = ' '.join(set(tags.split(' ')))
    
    GS.append([tags, title, url])
    return tags


def url_to_title(url):
    r = requests.get(url)
    html_txt = r.content.decode()
    soup = BeautifulSoup(html_txt, 'html5lib')
    if soup.title is None:
        title = '[Title not found]'
    else:
        title = soup.title.string
    return title.strip()


def upload_clipboard():
    print('Retrieving clipboard contents...')
    clipboard_txt = clipboard_get()
    if clipboard_txt.startswith('http'):
        print(f'Loading url: {clipboard_txt}')
        title = url_to_title(clipboard_txt)
        print(f'Using title: {title}')
        tags = upload_bookmark(GS, title, url=clipboard_txt)
        print(f'Tags: {tags}')
    else:
        print('Clipboard content is not a url:')
        print(f'{clipboard_txt}')
        return None


GS = open_spreadsheet()


if __name__ == "__main__":
    r = upload_clipboard()
    if r is None:
        GS.print_cell_data(i_start=-5)
