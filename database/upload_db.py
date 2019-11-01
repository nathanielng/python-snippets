#!/usr/bin/env python

# Uploads a .csv file to a PostgreSQL database

import argparse
import os
import pandas as pd

from sqlalchemy import create_engine


# ----- Utilities -----
def db_connect(dbstring):
    try:
        engine = create_engine(dbstring)
        return engine
    except Exception as e:
        print(f'Failed to connect to database {dbstring}')
        print(e)
        return None


def drop_table(engine, table_name):
    results = engine.execute(f'DROP TABLE IF EXISTS {str(table_name)}')
    return results


def upload(df, engine, table_name):
    try:
        drop_table(engine, table_name)
        df.to_sql(table_name, con=engine)
    except Exception as e:
        print('Failed to connect to database')
        print(e)


def view(engine, table_name):
    try:
        results = engine.execute(f'SELECT * FROM {table_name}')
        for r in results:
            print(r)
    except Exception as e:
        print(f'Failed to connect to database / table {table_name}')
        print(e)


# ----- Main Program -----
def main(args):
    filename = os.path.expanduser(args.file)
    df = pd.read_csv(filename)
    print(f"Loaded {filename} with {len(df)} rows") 
    db = db_connect(args.dbstring)
    if db is None:
        return
    upload(df, db, args.table)
    view(db, args.table)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='CSV file to upload')
    parser.add_argument('--dbstring', help='DB string in the format postgres://userid:passwd@hostname:port/db_name')
    parser.add_argument('--table', help='Name of the table')
    args = parser.parse_args()
    main(args)

