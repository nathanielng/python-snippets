#!/usr/bin/env python

import argparse
import requests


def get_data_from_url(url):
    """
    With a specified user agent, download data
    from a specified URL
    """
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    req = urllib.request.Request(url, data=None, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
           html = response.read()
    except urllib.error.HTTPError as e:
        print(f'HTTP Error, code={e.code}:')
        print(e.read())
    except urllib.error.URLError as e:
        print('URL Error:')
        print(e.reason)
    return html


def download_from_url(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    else:
        print(f"Unable to access {url}")
        print(f"Return code: {r.status_code}")
        return None


def download_file_from_url(url, filename):
    r = requests.get(url)
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(r.content)


def get_tables(url):
    """
    Downloads tables from a specified URL
    """
    html = get_data_from_url(url)
    dfs = pd.read_html(html.decode())
    return dfs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('csv')
    args = parser.parse_args()
    dfs = get_tables(args.url)
    if len(dfs) > 0:
        dfs[0].to_csv(args.csv)

