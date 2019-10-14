#!/bin/bash

# Removes the `-x` executable permissions set
# by OneDrive sync

export folders=`ls -d */ | xargs`
for folder in $folders; do
    chmod 755 "$folder"
    cd $folder
    chmod -x *.py *.sh
    cd ..
done
