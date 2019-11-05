#!/usr/bin/env python

import argparse
import selenium

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


# ----- Open Browser -----
try:
    browser = webdriver.Safari()
except Exception as e:
    print("Could not open Safari browser")
    print(f"Exception: {e}")
    quit()


# ----- Subroutines -----
def access_url(browser, url, xpath, timeout=10):
    browser.get(url)
    try:
        WebDriverWait(browser, timeout).until(
            expected_conditions.visibility_of_element_located(
            (By.XPATH, xpath))
        )
        return browser.find_elements_by_xpath(f"{xpath}")
    except TimeoutException as e:
        print(f"Exception: {e}")
        return None


def main(args):
    elms = access_url(browser, args.url, args.xpath)
    return elms


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--xpath')
    args = parser.parse_args()
    main(args)
 
