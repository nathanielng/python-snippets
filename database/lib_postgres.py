#!/usr/bin/env python

"""
This is a template for database access to PostgreSQL databases using
the psycopg2 library
"""

import os
import pandas as pd
import psycopg2

from psycopg2 import Error


DATABASE_URL = os.getenv('DATABASE_URL', default='postgresql://localhost')


class PostgresDB:

    def __init__(self, DATABASE_URL):
        self._conn = None
        try:
            self._conn = psycopg2.connect(DATABASE_URL)
        except Exception as e:
            print(f'Unable to connect to {DATABASE_URL}')
            print(e)
    
    def __str__(self):
        return f'PostgresDB connected at {DATABASE_URL}'

    def execute(self, cmd, action):
        cursor = self._conn.cursor()
        try:
            cursor.execute(cmd);
            r = None
            if action == 'fetchone':
                r = cursor.fetchone()
            elif action == 'fetchmany':
                r = cursor.fetchmany()
            elif action == 'fetchall':
                r = cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as e:
            print(f'Failed to execute "{cmd}"')
            print(f'Exception: {e}')
        finally:        
            cursor.close()
        return r

    def version(self):
        return self.execute('SELECT version();', action='fetchone')[0]

    def pandas_query(self, query):
        return pd.read_sql_query(query, self._conn)

    def tables(self):
        query = """SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"""
        return self.pandas_query(query)


if __name__ == "__main__":
    PDB = PostgresDB(DATABASE_URL)
    print(PDB)
    print(PDB.version())
    print(PDB.tables())

