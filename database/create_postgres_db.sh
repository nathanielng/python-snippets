#!/bin/bash
if [ "$1" = "" ]; then
    echo "Usage: $0 [database_name]"
    exit 1
else
    db_name="$1"
fi

createdb -O postgres $db_name
if [ "$?" -eq 0 ]; then
    echo "You may now connect to the database using:"
    echo "psql -U postgres -d ${db_name}"
else
    echo "Database creation failed"
fi

