#!/bin/bash

# Removes the `-x` executable permissions set
# by OneDrive sync

export folders=`ls -d */ | xargs`
for folder in $folders; do
    chmod 755 "$folder"
    cd $folder
    files=(*.sh)
    if [ -e "${files[0]}" ]; then
        chmod -x *.sh
    fi
    chmod -x *.py
    cd ..
done

