#!/usr/bin/env python

"""
This is a template for database access to PostgreSQL databases using
the psycopg2 library
"""

import os
import psycopg2

from psycopg2 import Error


DATABASE_URL = os.getenv('DATABASE_URL', default=None)


class PostgresDB:

    def __init__(self, DATABASE_URL):
        self._conn = None
        try:
            self._conn = psycopg2.connect(DATABASE_URL)
        except Exception as e:
            print(f'Unable to connect to {DATABASE_URL}')
            print(e)
    
    
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
        except Exception as e:
            print(f'Failed to execute "{cmd}"')
            print(f'Exception: {e}')
        
        cursor.close()
        return r


    def version(self):
        return self.execute('SELECT version();', action='fetchone')[0]


if __name__ == "__main__":
    PDB = PostgresDB(DATABASE_URL)
    print(PDB.version())
