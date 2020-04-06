#!/usr/bin/env python

import datetime
import os
import platform
import psutil
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


def print_cpu_info():
    print(f"Physical CPU count: {psutil.cpu_count(logical=False)}")
    print(f"Logical CPU count: {psutil.cpu_count(logical=True)}")
    print(f"CPU frequency: {psutil.cpu_freq().max/1000.0:.2f}Ghz\n")


def print_mem_info():
    factor = 1024*1024*1024 # kB > MB > GB
    vm = psutil.virtual_memory()
    print(f"Memory: {vm.available/factor:.2f} GB (available), {vm.used/factor:.2f} GB (used), {vm.total/factor:.1f} GB (total)")
    print(f"Memory Percentage: {vm.percent}%\n")


def print_boot_info():
    bt = datetime.datetime.fromtimestamp(psutil.boot_time())
    bt_str = bt.strftime('%B %d, %Y %H:%M')
    print(f"Boot time: {bt_str}\n")


if __name__ == "__main__":
    print_platform_info()
    print_cpu_info()
    print_mem_info()
    print_python_info()
    print_boot_info()
    print_script_info()
