#!/usr/bin/env python

import argparse
import boto3
import json


dynamo = boto3.resource('dynamodb')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--table', required=True)
    parser.add_argument('--id', required=True)
    parser.add_argument('--value')
    args = parser.parse_arges()

    table = dynamo.Table(args.table)
    table.load()

    if args.value:
        response = table.put_item(
            Item = {
                'Id': args.id
                'Value': args.value
            }
        )
    else:
        response = table.get_item(
             Key = {
                 'Id': args.id
             }
        )
    print(json.dumps(response, indent=2, default=str)
