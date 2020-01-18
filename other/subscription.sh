#!/bin/bash
# Example `usage for subscription.py

if [ -e "subscription.py" ]; then
    python subscription.py --start 10 --qty 10.5 --unit GB
else
    SCRIPT_DIR=`dirname "$0"`
    python ${SCRIPT_DIR}/subscription.py --start 10 --qty 10.5 --unit GB
fi
