#!/usr/bin/env python

import argparse
import os
import pandas as pd
import re
import sqlite3


class SqliteDB:

    def __init__(self, filename):
        self._dbfile = filename
        try:
            self._conn = sqlite3.connect(self._dbfile)
        except Exception as e:
            print(f'Unable to connect to {self._dbfile}')
            print(e)
            self._conn = None
            return

        try:
            self._cur = self._conn.cursor()
        except Exception as e:
            print(f'Unable to get cursor')
            print(f'Exception: {e}')
            self._cursor = None
            return


    def query(self, query, fetch='fetchall'):
        try:
            self._cur.execute(query)  # sqlite3.Cursor object
        except Exception as e:
            print(f'Exception: {e}')
            return None

        if fetch == 'fetchone':
            result = self._cur.fetchone()
        elif fetch == 'fetchall':
            result = self._cur.fetchall()
        return result


    def excecute(self, query, data):
        try:
            self._cur.execute(query, data)
        except Exception as e:
            print(f'Exception: {e}')
            return None
        return result


    def get_tables(self):
        """
        Retrieves table names
        """
        result = self.query("SELECT name FROM sqlite_master WHERE type = 'table'")
        tables = [ x[0] for x in result ]
        return tables


    def get_schema(self):
        """
        Retrieves table schema
        """
        result = self.query("SELECT sql FROM sqlite_master WHERE type = 'table'")
        tables = [ x[0] for x in result ]
        return tables


    def get_dataframe(self, table):
        """
        Retrieves entire dataframe
        Use query() to retrieve a partial dataframe
        """
        df = pd.read_sql_query(f'SELECT * from {table}', self._conn)
        return df


    def save_table(self, table, filename):
        """
        Retrieves table from database
        """
        df = self.get_dataframe(table)
        n = len(df)
        if filename.endswith('csv'):
            df.to_csv(filename, index=None)
        elif filename.endswith('xlsx'):
            df.to_excel(filename, index=None)
        print(f'Saved {n} rows to {filename}')


    def close():
        self._conn.close()


def table_name_from_schema(txt):
    m = re.search('CREATE TABLE "(.*)"', txt)
    if m is not None:
        return m.group(1)
    else:
        return None


def print_schema(schema):
    for s in schema:
        table = table_name_from_schema(s)
        if table is not None:
            print(f"----- Schema for: {table} -----")
        else:
            print(f"----- Schema -----")
        print(s)


def main(args):
    SQ = SqliteDB(args.database)

    if args.info is True:
        tables = SQ.get_tables()
        print(f"Tables: {', '.join(tables)}")
        schema = SQ.get_schema()
        print_schema(schema)

    if isinstance(args.save, str) and isinstance(args.table, str):
        SQ.save_table(args.table, args.save)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--database')
    parser.add_argument('--info', action='store_true')
    parser.add_argument('--table')
    parser.add_argument('--save')
    args = parser.parse_args()
    main(args)
