#!/usr/bin/env python

import argparse
import mechanize
import os
import webbrowser


def get_browser():
    browser = mechanize.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [("User-agent","Mozilla/5.0")]
    return browser


def browse_and_fill(url, boxes):
    """
    Browse to a website
    Fill each box
    """
    browser = get_browser()
    bot = browser.open(url)

    for box in boxes:
        if box == 'submit':
            response = browser.submit()
            content = response.read()
            data_to_be_sent = browser.get_data()
            print('Data to be send:')
            print(data_to_be_sent)
            return content

        tag, attribute, value = box.split(':')
        if tag == 'form':
            print(f'Found <{tag} {attribute}={value}> tag')
            if attribute == 'name':
                browser.select_form(name=value)
            elif attribute == 'id':
                browser.select_form(id_=lambda x: value in x)
            elif attribute == 'class':
                browser.select_form(class_=lambda x: value in x)
            else:
                print(f'Invalid attribute: {attribute}')
        elif tag == 'input':
            print(f'Found <{tag} {attribute}={value}> tag')
            variable, val = value.split('=')
            browser[variable] = val
        else:
            print(f'Invalid tag: {tag}')
            print(f'  attribute={attribute}')
            print(f'  value={value}')
    
    return content


def display_html(content, html_file='webscrape_results.html'):
    """
    Writes content to a html file and opens it in a browser
    """
    with open(html_file, 'w') as f:
        f.write(content)
    webbrowser.open(f'file://{os.path.realpath(html_file)}')

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--boxes')
    args = parser.parse_args()
    boxes = args.boxes.split(',')

    html = browse_and_fill(args.url, boxes)
    display_html(html.decode())
