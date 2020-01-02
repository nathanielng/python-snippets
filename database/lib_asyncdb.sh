#!/usr/bin/env python

if [ "$1" = "" ]; then
    echo "Usage: $0 [version|tables|databases]"
    exit
elif [ "$1" = "version" ]; then
    python lib_asyncdb.py --query 'SELECT version();'
elif [ "$1" = "tables" ]; then
    python lib_asyncdb.py --query "SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"
elif [ "$1" = "databases" ]; then
    python lib_asyncdb.py --query "SELECT datname from pg_database;"
fi

