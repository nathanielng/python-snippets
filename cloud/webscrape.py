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
    try:
       browser.get(url)
    except Exception as e:
        print(f'Exception: {e}')
        return False

    if xpath is None:
        return True

    try:
        WebDriverWait(browser, timeout).until(
            expected_conditions.visibility_of_element_located(
            (By.XPATH, xpath))
        )
        return True
    except TimeoutException as e:
        print(f'Failed to access url: {url}')
        print(f"Exception: {e}")
        return False


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


def parse_line(browser, i, line: list):
    """
    Parses a single line of code

    - `browseto|url|xpath`: browse to {url} until {xpath} is detected
    - `click|method|value`: click an element
    - `exec|method|variable>command`: execute script {command}
    - `input|method|variable>input_value`: fill input element with input_value
    - `select|method|variable>count`: go to dropdown element & scroll down by `count`
    - `setwindowsize|x|y`: set the window size to (x,y)
    - `scrollto|x|y`: scroll to (x,y)
    - `submit`: submit a form
    - `wait`: wait until element is available
    """
    tag, attribute, value = line

    if tag == 'browseto':
        if value == 'None':
            value = None
        print(f'{i}. Browsing to "{attribute}" until xpath="{value}" is detected"...')
        return access_url(browser, url=attribute, xpath=value)

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

    elif tag[:4] == 'exec':
        variable, command = split_value(value, '>')
        print(f'{i}. Executing script {command} on element ({attribute}: {variable})')
        element = find_element(method=attribute, variable=variable)
        if element is None:
            return False
        browser.execute_script(command, element)

    elif tag == 'input':
        variable, input_val = split_value(value, '>')
        print(f'{i}. Looking for "<{tag} {attribute}={variable}>"... textbox to fill with {input_val}')

        element = find_element(method=attribute, variable=variable)
        if element is None:
            return False
        try:
            if input_val == 'tab':
                element.send_keys(Keys.TAB)
            else:
                element.send_keys(input_val)
        except Exception as e:
            print(f'Exception: {e}')
            return False

    elif tag == 'select':
        variable, match_str = split_value(value, '>')
        print(f'{i}. Looking for "<{tag} {attribute}={variable}>"... dropdown with {match_str}')
        time.sleep(3)
        elements = find_elements(method=attribute, variable=variable)
        if len(elements) == 0:
            print('select failed: element not found')
            return False

        for ii, element in enumerate(elements):
            print(f' - {ii}: element.text={element.text}')
            if element.text == match_str:
                element.click()
                print('(CLICK)')
                return True

        print('Failed to find a matching element')
        return False

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
        try:
            element = find_element(method=attribute, variable=value)
        except Exception as e:
            print('submit failed: element not found')
            print(f'Exception: {e}')
            return False

        x = input('Submit? (y/n) ')
        if x.lower() == 'y':
            try:
                element.click()
                print('Form was submitted')
            except Exception as e:
                print(f'Submission error: {e}')
                return False
        else:
            print('Submission cancelled by user')
            return False

    elif tag == 'wait':
        print(f'{i}. Waiting for expected condition: "{attribute}={value}"...')
        ec = create_expected_condition(method=attribute, variable=value)
        try:
            WebDriverWait(browser, 10).until(
                expected_conditions.visibility_of_element_located(ec)
            )
        except TimeoutException:
            print('TimeoutException')
            return False

    else:
        print(f'{i}. Invalid tag: {tag}, attribute={attribute}, value={value}')
        return False

    return True


def sanitize_line_input(i, line):
    if line[0] == '#' or line[0] == '':
        # Skip commented lines and blank lines
        return None
    elif line[0] == 'sleep':
        t = int(line[1])
        print(f'{i}: Sleep for {t} seconds')
        time.sleep(t)
        return None
    elif len(line) != 3:
        print(f'Error: line #{i} does not have 3 elements:')
        print(line)
        return None

    return line


def parse_code_block(browser, codes):
    """
    Parses a block of code
    """

    for i, code in enumerate(codes):
        line = code.split('|')
        line = sanitize_line_input(i, line)
        if line is None:
            continue
        else:
            r = parse_line(browser, i, line)

    return r


def parse_prompt(browser):
    """
    User enters instructions at a prompt
    """
    i = 0
    while True:
        line = input('webscrape> ')
        if line in ['break', 'exit', 'quit']:
            break

        i += 1
        line = sanitize_line_input(i, line)
        if line is None:
            continue
        else:
            r = parse_line(browser, i, line)


def run_code_file(browser, code_file):
    with open(code_file) as f:
        codes = f.read()
    codes = codes.split('\n')
    return parse_code_block(browser, codes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--browser', default='chrome', help='Browser')
    parser.add_argument('--code_file', default='', help="Code File")
    args = parser.parse_args()

    browser = open_browser(args.browser.lower())
    if args.code_file == '':
        parse_prompt(browser)
    else:
        r = run_code_file(browser, args.code_file)

    x = input('Quit browser? (y/n) ')
    if x.lower() == 'y':
        browser.quit()
