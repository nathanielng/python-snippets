#!/usr/bin/env python

import argparse
import os
import selenium
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


# ----- Open Browser -----
def open_chrome():
    driver_path = os.path.abspath('chromedriver')
    try:
        browser = webdriver.Chrome(driver_path)
        return browser
    except Exception as e:
        print(f"Could not find ChromeDriver at {driver_path}")
        print("ChromeDriver may be downloaded from https://chromedriver.chromium.org")
        print(f"The executable should be copied to the location: {driver_path}")
        print(f"Exception: {e}")
        return None


def open_safari():
    try:
        browser = webdriver.Safari()
        return browser
    except Exception as e:
        print("Could not open Safari browser")
        print(f"Exception: {e}")
        return None


# ----- Subroutines -----
def login(browser, url, userid, token, elm_id_userid, elm_id_token, timeout=10):
    browser.get(url)
    time.sleep(2)
    userid_box = browser.find_element_by_id(elm_id_userid)
    userid_box.send_keys(userid)
    token_box = browser.find_element_by_id(elm_id_token)
    token_box.send_keys(token)
    token_box.submit()


def access_url(browser, url, xpath, timeout=10):
    browser.get(url)
    time.sleep(2)
    try:
        WebDriverWait(browser, timeout).until(
            expected_conditions.visibility_of_element_located(
            (By.XPATH, xpath))
        )
        return browser.find_elements_by_xpath(f"{xpath}")
    except TimeoutException as e:
        print(f"Exception: {e}")
        return None


def print_params(args):
    print(f"Brower: {args.browser}")
    print(f"elm_id_userid: {args.elm_id_userid}")
    print(f"elm_id_token: {args.elm_id_token}")
    print(f"login: {args.login}")
    print(f"token: {args.token}")
    print(f"url: {args.url}")
    print(f"userid: {args.userid}")


def main(args):
    print_params(args)

    if args.browser == 'safari':
        browser = open_safari()
    else:
        browser = open_chrome()
    if browser is None:
        quit()

    login(browser, args.login, args.userid, args.token,
          args.elm_id_userid, args.elm_id_token)
    time.sleep(3)

    elms = access_url(browser, args.url, args.xpath)
    return elms


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', default='chrome', help='Browser')
    parser.add_argument('--elm_id_userid', help="UserID Element ID")
    parser.add_argument('--elm_id_token', help="Token Element ID")
    parser.add_argument('--login', help="Login URL")
    parser.add_argument('--token', help="Token")
    parser.add_argument('--url', help="URL")
    parser.add_argument('--userid', help="User ID")
    parser.add_argument('--xpath')
    args = parser.parse_args()
    main(args)
 
