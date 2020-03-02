#!/bin/bash

for file in *
do
    OLD_FILENAME="$file"
    NEW_FILENAME=`echo "$file" | tr -d '|'`
    if [[ ! "$OLD_FILENAME" = "$NEW_FILENAME" ]]; then
        mv -i "$OLD_FILENAME" "${NEW_FILENAME}"
    else
        echo "Skipping mv -i rename for:"
        echo "  old: \"$OLD_FILENAME\""
        echo "  new: \"${NEW_FILENAME}\""
    fi
done
