#!/usr/bin/env python

import argparse
import os
import selenium
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait


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


def open_browser(browser_name):
    try:
        if browser_name == 'safari':
            browser = open_safari()
        else:
            browser = open_chrome()
    except Exception as e:
        print('Could not open browser')
        print(f'Exception: {e}')
        quit()
    return browser


# ----- Subroutines -----
def access_url(browser, url, xpath=None, timeout=10):
    browser.get(url)
    if xpath is None:
        return

    try:
        WebDriverWait(browser, timeout).until(
            expected_conditions.visibility_of_element_located(
            (By.XPATH, xpath))
        )
        return
    except TimeoutException as e:
        print(f'Failed to access url: {url}')
        print(f"Exception: {e}")
        return


def find_element(method, variable):
    if method == 'class':
        element = browser.find_element_by_class_name(variable)
    elif method == 'css':
        element = browser.find_element_by_css_selector(variable)
    elif method == 'id':
        element = browser.find_element_by_id(variable)
    elif method == 'name':
        element = browser.find_element_by_name(variable)
    elif method == 'tag':
        element = browser.find_element_by_tag(variable)
    elif method == 'xpath':
        element = browser.find_element_by_xpath(variable)
    return element


def find_elements(method, variable):
    if method == 'class':
        elements = browser.find_elements_by_class_name(variable)
    elif method == 'css':
        elements = browser.find_elements_by_css_selector(variable)
    elif method == 'name':
        elements = browser.find_elements_by_name(variable)
    elif method == 'tag':
        elements = browser.find_elements_by_tag(variable)
    elif method == 'xpath':
        elements = browser.find_elements_by_xpath(variable)
    return elements


def parse_code(browser, codes):
    """
    Browse to a website using selenium webdriver
    Follows a list of codes for the actions to take

    - `browseto|url|xpath`: browse to a url until xpath is detected
    - `input|attribute|value>input_value`: fill input element with input_value
    - `click|attribute|value`: click an element
    - `submit`: submit a form
    """

    for i, code in enumerate(codes):
        line = code.split('|')
        if line[0] == '#' or line[0] == '':
            # Skip commented lines and blank lines
            continue
        elif line[0] == 'pause':
            time.sleep(int(line[1]))
            continue
        elif len(line) != 3:
            print(f'Error: line #{i} does not have 3 elements:')
            print(line)
            continue
        tag, attribute, value = line

        if tag == 'browseto':
            if value == 'None':
                value = None
            print(f'Browsing to "{attribute}" until xpath="{value}" is detected"...')
            access_url(browser, url=attribute, xpath=value)
        elif tag == 'input':
            assignment = value.split('>')
            if len(assignment) != 2:
                print(f'Error: assignment does not have 2 elements:')
                print(assignment)
                continue
            variable, input_val = assignment
            print(f'Looking for "<{tag} {attribute}={variable}>"... to fill with {input_val}')

            element = find_element(method=attribute, variable=variable)
            element.send_keys(input_val)
        elif tag == 'click':
            print(f'Clicking on "{attribute}={value}"...')
            element = find_element(method=attribute, variable=value)
            # assert element.get_attribute('type') == 'radio'
            element.click()

        elif tag == 'submit':
            print(f'Submitting "{attribute}={value}"...')
            element = find_element(method=attribute, variable=value)
            element.submit()
        else:
            print(f'Invalid tag: {tag}')
            print(f'  attribute={attribute}')
            print(f'  value={value}')

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', default='chrome', help='Browser')
    parser.add_argument('--code_file', help="Code File")
    args = parser.parse_args()

    with open(args.code_file) as f:
        codes = f.read()
    codes = codes.split('\n')

    browser = open_browser(args.browser.lower())
    parse_code(browser, codes)
    browser.quit()
