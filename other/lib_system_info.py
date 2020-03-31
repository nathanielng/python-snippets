#!/usr/bin/env python

import os
import platform
import site
import sys


def print_platform_info():
    print(f'OS: {os.uname()}')
    print(f'Platform: {platform.platform()}')
    print(f'Version: {platform.version()}')
    print(f'System: {platform.system()}')
    print(f'Processor: {platform.processor()}')
    print(f'Machine Type: {platform.machine()}')
    print(f'Architecture: {platform.architecture()[0]}\n')


def print_python_info():
    print(f'Prefix: {sys.prefix}\n')
    print(f'Python Version:\n{sys.version}\n')
    print(f'Site Packages:\n{site.getsitepackages()}\n')


def print_script_info():
    print(f'This Script:\n{os.path.realpath(__file__)}')
    print(f'__file__ == {__file__}')
    print(f'__name__ == {__name__}')


if __name__ == "__main__":
    print_platform_info()
    print_python_info()
    print_script_info()
