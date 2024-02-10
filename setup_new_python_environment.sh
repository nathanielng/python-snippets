#!/bin/bash

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
