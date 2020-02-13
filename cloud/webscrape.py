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
        quit()
        return None


def open_safari():
    driver_path = '/usr/bin/safaridriver'
    try:
        browser = webdriver.Safari(executable_path=driver_path)
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


def create_expected_condition(method, variable):
    if method == 'class':
        mthd = By.CLASS_NAME
    elif method == 'css':
        mthd = By.CSS_SELECTOR
    elif method == 'id':
        mthd = By.ID
    elif method == 'link_text':
        mthd = By.LINK_TEXT
    elif method == 'name':
        mthd = By.NAME
    elif method == 'partial_link_text':
        mthd = By.PARTIAL_LINK_TEXT
    elif method == 'tag':
        mthd = By.TAG_NAME
    elif method == 'xpath':
        mthd = By.XPATH
    else:
        mthd = None
    return mthd, variable


def find_element(method, variable):
    try:
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
    except selenium.common.exceptions.NoSuchElementException as e:
        print(f'No such element: find_element_by_{method}[...]({variable})')
        print(f'Exception: {e}')
        return None


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


def split_value(value, split_char='>'):
    assignment = value.split(split_char)
    return '>'.join(assignment[:-1]), assignment[-1]


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
            t = int(line[1])
            print(f'{i}: Pause for {t} seconds')
            time.sleep(t)
            continue
        elif len(line) != 3:
            print(f'Error: line #{i} does not have 3 elements:')
            print(line)
            continue
        tag, attribute, value = line

        if tag == 'browseto':
            if value == 'None':
                value = None
            print(f'{i}. Browsing to "{attribute}" until xpath="{value}" is detected"...')
            access_url(browser, url=attribute, xpath=value)

        elif tag == 'click':
            print(f'{i}. Clicking on "{attribute}={value}"...')
            element = find_element(method=attribute, variable=value)
            # assert element.get_attribute('type') == 'radio'
            if element is None:
                return False
            try:
                element.click()
            except selenium.common.exceptions.ElementNotInteractableException as e:
                print("Exception: selenium.common.exceptions.ElementNotInteractableException")
                print(e)
                return False

        elif tag == 'execute':
            variable, input_val = split_value(value, '>')
            element = find_element(method=attribute, variable=variable)
            if element is None:
                return False
            browser.execute_script(input_val, element)

        elif tag == 'input':
            variable, input_val = split_value(value, '>')
            print(f'{i}. Looking for "<{tag} {attribute}={variable}>"... textbox to fill with {input_val}')

            element = find_element(method=attribute, variable=variable)
            if element is None:
                return False
            if input_val == 'tab':
                element.send_keys(Keys.TAB)
            else:
                element.send_keys(input_val)

        elif tag == 'select':
            variable, input_val = split_value(value, '>')
            print(f'{i}. Looking for "<{tag} {attribute}={variable}>"... dropdown with {input_val}')
            time.sleep(3)
            elements = find_elements(method=attribute, variable=variable)
            if len(elements) == 0:
                print('Element not found')
                return False

            for ii, element in enumerate(elements):
                print(f' - {ii}: element.text={element.text}')
                if element.text == input_val:
                    element.click()
                    print('(CLICK)')
                    break

        elif tag == 'scrollto':
            x = int(attribute)
            y = int(value)
            print(f'{i}. Scrolling to ({x},{y})...')
            browser.execute_script(f'window.scrollTo({x},{y})')

        elif tag == 'setwindowsize':
            x = int(attribute)
            y = int(value)
            print(f'{i}. Setting window size to ({x},{y})...')
            browser.set_window_size(x, y)

        elif tag == 'submit':
            print(f'{i}. Submitting "{attribute}={value}"...')
            element = find_element(method=attribute, variable=value)
            element.submit()

        elif tag == 'wait':
            ec = create_expected_condition(method=attribute, variable=value)
            try:
                WebdriverWait(browser, 10).until(
                    expected_conditions.visibility_of_element_located(ec)
                )
            except TimeoutException:
                print('TimeoutException')

        else:
            print(f'{i}. Invalid tag: {tag}, attribute={attribute}, value={value}')

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', default='chrome', help='Browser')
    parser.add_argument('--code_file', help="Code File")
    args = parser.parse_args()

    with open(args.code_file) as f:
        codes = f.read()
    codes = codes.split('\n')

    browser = open_browser(args.browser.lower())
    success = parse_code(browser, codes)
    x = input('Quit browser? (y/n) ')
    if x.lower() == 'y':
        browser.quit()
