#!/bin/bash

# Download this file with either of the following:
# wget https://raw.githubusercontent.com/nathanielng/python-snippets/master/setup_new_python_environment.sh
# curl -O https://raw.githubusercontent.com/nathanielng/python-snippets/master/setup_new_python_environment.sh

# Run this file with:
# sh setup_new_python_environment.sh [env_name]

if [ "$1" = "" ]; then
    echo "Usage: $0 [env_name]"
    exit 1
fi

ENV_NAME="$1"

curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
python3 -m pip install virtualenv
virtualenv $ENV_NAME
source $ENV_NAME/bin/activate
