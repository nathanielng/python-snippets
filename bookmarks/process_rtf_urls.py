#!/usr/bin/env python

# Parses RTF files, looking for hyperlinks in the following format
# {\field{\*\fldinst{HYPERLINK "https://www.example.com/"}}{\fldrslt \f1\fs26 \cf2 URL Title}}


import argparse
import pandas as pd
import re


def process_rtf(filename):
    with open(filename, 'r') as f:
        rtf_text = f.read()

    pattern = r"\{\\field\{\\\*\\fldinst\{HYPERLINK\s*\"(.*?)\"\s*\}\}\{\\fldrslt\s*\\f1\\fs26\s*\\cf2\s*(.*?)\}"
    matches = re.findall(pattern, rtf_text, re.MULTILINE)
    urls = []
    titles = []
    for match in matches:
        url = match[0]
        title = match[1]
        print(f'{url},"{title}"')
        urls.append(url)
        titles.append(title)

    return {
        'url': urls,
        'title': titles
    }


def test_regex():
    # From an RTF file, copy and paste the hyperlink text into the string below,
    # replacing all '\' with a '\\'
    rtf_text = """{\\field{\\*\\fldinst{HYPERLINK "https://www.example.com/"}}{\\fldrslt \\f1\\fs26 \\cf2 URL Title}}"""
    # pattern = r"\{(.*?)\}"  # Detects text within curly braces
    # pattern = r"\{\\field\{(.*?)\}"
    # pattern = r"\{\\field\{\\\*\\fldinst\{(.*?)\}"
    pattern = r"\{\\field\{\\\*\\fldinst\{HYPERLINK\s*\"(.*?)\"\s*\}\}\{\\fldrslt\s*\\f1\\fs26\s*\\cf2\s*(.*?)\}"
    matches = re.findall(pattern, rtf_text)

    for match in matches:
        url = match[0]
        url_text = match[1]
        assert url == "https://www.example.com/"
        assert url_text == "URL Title"



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, default='urls.rtf')
    parser.add_argument('--output', type=str, default='urls.csv')
    args = parser.parse_args()

    test_regex()
    df = process_rtf(args.file)
    df = pd.DataFrame(df)
    df.to_csv(args.output, index=False)
