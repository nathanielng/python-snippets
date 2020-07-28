#!/usr/bin/env python

import argparse
import os

from sqlalchemy import create_engine, inspect


DATABASE_URL = os.getenv('DATABASE_URL', default='sqlite:///sqlite_data.db')
engine = create_engine(DATABASE_URL)


def execute_raw_query(engine, query):
    engine.execute(query)


def get_tables(engine):
    inspector = inspect(engine)
    return inspector.get_table_names()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', default='', help='SQL query')
    parser.add_argument('--tables', action='store_true')
    args = parser.parse_args()

    if args.tables:
        tables = get_tables(engine)
        print(tables)

    if args.query != '':
        execute_raw_query(engine, args.query)
