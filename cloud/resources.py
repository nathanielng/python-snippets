#!/usr/bin/env python

import argparse
import boto3
import datetime
import json


sts = boto3.client('sts')


def get_session(account_id, service):
    response = sts.assume_role(
        RoleArn=f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole',
        RoleSessionName='newsession'
    )
    success = response['ResponseMetadata']['HTTPStatusCode']
    if success != 200:
        print('Error: failed to assume role.\nResponse:\n')
        print(json.dumps(response, indent=2, default=str))
        exit()
    else:
        new_credentials = response['Credentials']

    assumed_client = boto3.client(
        service,
        aws_access_key_id = new_credentials['AccessKeyId'],
        aws_secret_access_key = new_credentials['SecretAccessKey'],
        aws_session_token = new_credentials['SessionToken']
    )
    return assumed_client


def get_s3_buckets(s3_client):
    response = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return buckets


def get_ec2_instances(ec2_client, region):
    response = ec2_client.describe_instances()
    if len(response['Reservations']) == 0:
        return []
    instances_json = response['Reservations'][0]['Instances']
    instances_dict = []
    for instance in instances_json:
        instances_dict.append({
            'Id': instance['InstanceId'],
            'Type': instance['InstanceType'],
            'State': instance['State']['Name'],
            'Region': region
        })
    return instances_dict


def get_monthly_spend(ce_client, start_date=None, end_date=None):
    now = datetime.datetime.now()
    if start_date is None:
        start_date = now.strftime('%Y-%m-01')
    if end_date is None:
        end_date = now.strftime('%Y-%m-%d')

    r = ce_client.get_cost_and_usage(
        TimePeriod={'Start': start_date, 'End': end_date},
        Granularity='MONTHLY',
        Metrics=['BlendedCost'])
    cost = r['ResultsByTime'][0]['Total']['BlendedCost']
    return f"{cost['Unit']} {float(cost['Amount']):.2f}"


def check_s3(s3_client):
    s3_buckets = get_s3_buckets(s3_client)
    print(f'S3 Buckets:\n{",".join(s3_buckets)}')


def check_ec2(ec2_client, regions):
    ec2_instances = []
    for region in regions:
        instances = get_ec2_instances(ec2_client, region)
        ec2_instances += instances

    if len(ec2_instances) == 0:
        print(f'EC2 Instances: none')
    else:
        print(f'EC2 Instances:')
        print('Id                  |  Type      | State    | Region')
        for ec2 in ec2_instances:
            print(ec2_instances)
            print(f'{ec2["Id"]} | {ec2["Type"]:10s} | {ec2["State"]:8s} | {ec2["Region"]}')


def check_monthly_spend(ce_client):
    monthly_spend = get_monthly_spend(ce_client)
    print(f'Spend: {monthly_spend}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--account_id', type=int, required=True)
    parser.add_argument('--check_s3', action='store_true')
    parser.add_argument('--check_ec2', type=str)
    parser.add_argument('--check_monthly_spend', action='store_true')
    args = parser.parse_args()

    if args.check_s3:
        client = get_session(args.account_id, 's3')
        check_s3(client)

    if args.check_ec2:
        regions = args.check_ec2.split(',')
        client = get_session(args.account_id, 'ec2')
        check_ec2(client, regions)

    if args.check_monthly_spend:
        client = get_session(args.account_id, 'ce')
        check_monthly_spend(client)
