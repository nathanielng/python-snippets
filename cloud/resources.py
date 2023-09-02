#!/usr/bin/env python

import argparse
import boto3
import datetime
import json


sts = boto3.client('sts')


def get_session(account_id):
    response = sts.assume_role(
        RoleArn=f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole',
        RoleSessionName='newsession'
    )
    success = response['ResponseMetadata']['HTTPStatusCode']
    if success != 200:
        print('Error: failed to assume role.\nResponse:\n')
        print(json.dumps(response, indent=2, default=str))
        exit()

    assumed_role_session = boto3.Session()
    response = assumed_role_session.client('sts').get_caller_identity()
    success = response['ResponseMetadata']['HTTPStatusCode']
    if success != 200:
        print('Error: failed to get client.\nResponse:\n')
        print(json.dumps(response, indent=2, default=str))
        exit()
    return assumed_role_session


def get_s3_buckets(s3_client):
    response = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return buckets


def get_ec2_instances(ec2_client):
    response = ec2_client.describe_instances()
    instances_json = response['Reservations'][0]['Instances']
    instances_dict = []
    for instance in instances_json:
        instances_dict.append({
            'Id': instance['InstanceId'],
            'Type': instance['InstanceType'],
            'State': instance['State']['Name']
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


def check_s3(session):
    s3_client = session.client('s3')
    s3_buckets = get_s3_buckets(s3_client)
    print(f'S3 Buckets:\n{s3_buckets}')


def check_ec2(session, regions):
    print(f'EC2 Instances:\n')
    print('Id                  |  Type      | State    | Region')
    for region in regions:
        ec2_client = session.client('ec2', region_name=region)
        ec2_instances = get_ec2_instances(ec2_client)
        for ec2 in ec2_instances:
            print(f'{ec2["Id"]} | {ec2["Type"]:10s} | {ec2["State"]:8s} | {region}')


def check_monthly_spend(session):
    ce_client = session.client('ce')
    monthly_spend = get_monthly_spend(ce_client)
    print(f'Spend: {monthly_spend}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--account_id', type=int, required=True)
    parser.add_argument('--check_s3', action='store_true')
    parser.add_argument('--check_ec2', type=str)
    parser.add_argument('--check_monthly_spend', action='store_true')
    args = parser.parse_args()

    session = get_session(args.account_id)
    if args.check_s3:
        check_s3(session)

    if args.check_ec2:
        regions = args.check_ec2.split(',')
        check_ec2(session, regions)

    if args.check_monthly_spend:
        check_monthly_spend(session)
