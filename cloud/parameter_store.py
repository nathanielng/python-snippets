#!/usr/bin/env python

import argparse
import boto3
import dotenv
import getpass
import logging
import os
import re
import time
import sys

from encrypt_text import decrypt_text

# Enhanced color palette
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
ORANGE = '\033[38;5;208m'
PINK = '\033[38;5;206m'
TEAL = '\033[38;5;45m'
LIME = '\033[38;5;118m'
RESET = '\033[0m'

# Text styles
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
ITALIC = '\033[3m'

# Background colors
BG_BLACK = '\033[40m'
BG_RED = '\033[41m'
BG_GREEN = '\033[42m'
BG_BLUE = '\033[44m'

DOT_ENV_PATH = os.getenv('DOT_ENV_PATH', None)
if DOT_ENV_PATH is None:
    print(f"{RED}Warning: DOT_ENV_PATH is not set{RESET}")
    config = dotenv.dotenv_values()
else:
    config = dotenv.dotenv_values(DOT_ENV_PATH)

aws_secret_access_key_encrypted = config.get('AWS_IAM_SECRET', None)
if aws_secret_access_key_encrypted is None:
    print(f"{RED}Error: AWS_IAM_SECRET is not set{RESET}")
    sys.exit(1)
aws_secret_access_key = decrypt_text(
    aws_secret_access_key_encrypted,
    getpass.getpass("Enter decryption password: ")
)

ssm = boto3.client(
    service_name = 'ssm',
    region_name = config.get('AWS_REGION'),
    aws_access_key_id = config.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key = aws_secret_access_key,
    aws_account_id = config.get('AWS_ACCOUNT_ID')
)

# Configure boto3 to log resource-related operations at INFO level
boto3.set_stream_logger('boto3.resources', logging.INFO)

def print_fancy_header(title, color=PINK, border_color=CYAN, width=60):
    """Print a fancy header with the given title."""
    print(f"\n{border_color}{'═'*width}{RESET}")
    print(f"{color}{BOLD}✧ {title} ✧{RESET}".center(width+15))
    print(f"{border_color}{'═'*width}{RESET}\n")

def get_key_file(key_name):
    return ssm.get_parameter(
        Name=key_name,
        WithDecryption=True
    ).get('Parameter').get('Value')

def parse_line(env_var_string):
    pattern = r'(?:export\s+)?(\w+)=(?:"([^"]+)"|\'([^\']+)\'|([^\s]+))'
    match = re.search(pattern, env_var_string)
    if match:
        key = match.group(1)
        # Value could be in group 2 (double quotes), 3 (single quotes), or 4 (no quotes)
        value = match.group(2) or match.group(3) or match.group(4)
        return key, value
    else:
        return '', ''

def print_login_file(key_name):
    print_fancy_header("LOGIN INFORMATION", PURPLE, TEAL)
    
    lines = get_key_file(key_name).split('\n')
    for line in lines:
        if line.startswith('# '):
            print(f'{TEAL}{BOLD}➤ {line[2:]}{RESET}')
        else:
            print(f'  {BLUE}{line}{RESET}')
    
    print(f"\n{TEAL}{'─'*60}{RESET}")

def print_key_file(key_name):
    print_fancy_header("KEY VALUES", ORANGE, GREEN)
    key_list = get_key_file(key_name).split('\n')
    
    # Count valid keys and skipped lines
    valid_keys = 0
    skipped_lines = 0
    
    for x in key_list:
        k, v = parse_line(x)
        if k:
            valid_keys += 1
            print(f'{BOLD}{RED}{k}{RESET}="{YELLOW}{v}{RESET}"')
        else:
            if x.strip():  # Only print non-empty lines
                skipped_lines += 1
                print(f'{PINK}⚠ {ITALIC}Skipping:{RESET} "{CYAN}{x}{RESET}"')
    
    print(f"\n{GREEN}{'─'*60}{RESET}")
    print(f"  {CYAN}Summary:{RESET} {GREEN}{valid_keys}{RESET} valid keys, {YELLOW}{skipped_lines}{RESET} skipped lines")
    print(f"{GREEN}{'─'*60}{RESET}")

def append_new_keys(key_text, old_key, new_key, sort=False):
    print_fancy_header("APPENDING KEYS", GREEN, TEAL)
    
    key_list = get_key_file(old_key).split('\n')
    new_keys = key_text.split('\n')
    key_list = key_list + new_keys
    key_list = [k for k in key_list if len(k) > 0]
    
    if sort:
        print(f"\n{YELLOW}Sorting and removing duplicates...{RESET}")
        time.sleep(0.5)
        key_list = list(set(key_list))
        key_list.sort()
        print(f"{GREEN}✓ Sort complete{RESET}")

    key_list = '\n'.join(key_list)
    
    print(f"\n{CYAN}Saving to parameter store...{RESET}")
    time.sleep(0.5)
    ssm.put_parameter(Name=new_key, Value=key_list, Type='SecureString', Overwrite=True)
    
    print(f"\n{BG_GREEN}{WHITE}{BOLD} SUCCESS {RESET}")
    print(f"\n{TEAL}{'✓'*20}{RESET}")
    print(f"{GREEN}{BOLD}Keys successfully appended!{RESET}")
    print(f"{TEAL}{'✓'*20}{RESET}\n")
    print(f"  {CYAN}From:{RESET} {old_key}")
    print(f"  {CYAN}To:{RESET}   {new_key}")
    print(f"  {CYAN}Added:{RESET} {YELLOW}{len(new_keys)}{RESET} new entries")
    print(f"  {CYAN}Total:{RESET} {GREEN}{len(key_list.split(chr(10)))}{RESET} entries\n")

def add_new_key(key_text, new_key):
    print_fancy_header("CREATING NEW KEY", LIME, PURPLE)
    
    entries = key_text.split('\n')
       
    print(f"\n{CYAN}Saving to parameter store...{RESET}")
    time.sleep(0.5)
    
    ssm.put_parameter(
        Name=new_key,
        Value=entries,
        Type='SecureString',
        Overwrite=True
    )
    
    print(f"\n{BG_BLUE}{WHITE}{BOLD} COMPLETE {RESET}")
    print(f"\n{PURPLE}{'★'*20}{RESET}")
    print(f"{GREEN}{BOLD}New key successfully created!{RESET}")
    print(f"{PURPLE}{'★'*20}{RESET}\n")
    print(f"  {CYAN}Key:{RESET} {UNDERLINE}{new_key}{RESET}")
    print(f"  {CYAN}Entries:{RESET} {YELLOW}{len(entries)}{RESET}")
    
    # Show a sample of the first few entries if there are many
    if len(entries) > 3:
        print(f"\n{TEAL}Sample of entries:{RESET}")
        for i, entry in enumerate(entries[:3]):
            print(f"  {LIME}{i+1}.{RESET} {CYAN}{entry}{RESET}")
        print(f"  {LIME}...{RESET} {CYAN}and {len(entries)-3} more{RESET}")
    print()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'{BOLD}{CYAN}AWS Parameter Store Utility{RESET}')
    parser.add_argument('--old_key', default = config.get('KEYVALUES_PARAMETER_PATH1'), help='Source parameter key')
    parser.add_argument('--new_key', default = config.get('KEYVALUES_PARAMETER_PATH2'), help='Destination parameter key')
    parser.add_argument('--key_text', default='', help='Text to add to parameter')
    parser.add_argument('--logins', action='store_true', help='Display login information')
    parser.add_argument('--sort', action='store_true', help='Sort keys and remove duplicates')
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()

    if args.key_text:
        append_new_keys(args.key_text, args.old_key, args.new_key, args.sort)

    if args.logins or args.all:
        print_login_file(config.get('LOGIN_PARAMETER_PATH'))

    if args.all:
        print_key_file(args.old_key)

    # Show current time
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{YELLOW}Execution time:{RESET} {current_time}\n")
