#!/usr/bin/env python

import argparse
import asyncio
import asyncpg
import os


DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL is None:
    print("No database URL found")
    quit()


async def exec_query(query_str):
    conn = await asyncpg.connect(DATABASE_URL)
    values = await conn.fetch(query_str)
    await conn.close()
    for i, value in enumerate(values):
        x = list(value.values())
        print(f"{i}: {x}")
    return values


def main(query):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(exec_query(query))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query')
    args = parser.parse_args()
    main(args.query)

