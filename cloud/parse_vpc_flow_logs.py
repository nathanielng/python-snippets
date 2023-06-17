#!/usr/bin/env python

import argparse
import boto3
import datetime
import json
import os
import pandas as pd

from dotenv import load_dotenv


now = datetime.datetime.now()
YEAR = now.year
MONTH = now.month
DAY = now.day

load_dotenv()
S3_BUCKET = os.getenv('S3_BUCKET', default=None)
S3_BUCKET_PREFIX = os.getenv('S3_BUCKET_PREFIX', default=None)
FILE_PREFIX = f'{S3_BUCKET_PREFIX}/{YEAR}/{MONTH:02d}/{DAY:02d}'
DEFAULT_CSV_FILE = f'{S3_BUCKET}-{YEAR}-{MONTH:02d}-{DAY:02d}.csv'

s3 = boto3.client('s3')


class S3Folder():

    def __init__(self, bucket=S3_BUCKET, prefix=FILE_PREFIX):
        self.bucket=bucket
        self.prefix=prefix
        self.keys=None
        self.final_df=None


    def list_objects(self):
        r = s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=f'{self.prefix}/',
        )
        self.keys = [ obj['Key'] for obj in r['Contents']]
        return self.keys


    def consolidate_objects(self, csv_file):
        if self.keys is None:
            self.keys = self.list_objects()

        df_list = []
        for key in self.keys:

            # Download Parquet File
            print(f'Downloading: s3://{self.bucket}/{key}')
            body = s3.get_object(Bucket=self.bucket, Key=f'{key}')['Body'].read()
            pq_file = os.path.basename(key)
            with open(pq_file, 'wb') as f:
                f.write(body)

            # Read Parquet File
            df = pd.read_parquet(pq_file)
            print(df)
            df_list.append(df)
            os.remove(pq_file)

        self.final_df = pd.concat(df_list)
        self.final_df.to_csv(csv_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--consolidate', action='store_true')
    parser.add_argument('--analyze', action='store_true')
    parser.add_argument('--csv_file', default=DEFAULT_CSV_FILE)
    args = parser.parse_args()

    if args.consolidate:
        s3f = S3Folder(
            bucket=S3_BUCKET,
            prefix=FILE_PREFIX
            )
        print(f"""Files: {','.join(s3f.list_objects())}""")
        s3f.consolidate_objects(csv_file=DEFAULT_CSV_FILE)

    elif args.analyze:
        df = pd.read_csv(args.csv_file)
        df.sort_values('bytes', ascending=False, inplace=True)
        df['utc-start'] = pd.to_datetime(df['start'],unit='s')
        df['utc-end'] = pd.to_datetime(df['end'],unit='s')
        df['megabytes'] = df['bytes'] / 1.0e6
        df['gigabytes'] = df['bytes'] / 1.0e9
        print(df.head().T)
