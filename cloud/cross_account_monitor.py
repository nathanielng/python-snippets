#!/bin/bash

import argparse
import boto3
import datetime
import json
import os

# Example usage:
# python  cross_account_monitor.py --account_ids ${AWS_ACCOUNT_IDS}

# Requires `OrganizationAccountAccessRole` with the following **Trust relationship**
# Replace ${account_id} with the actual account ID of the management AWS Account that will
# federate into sub-accounts and check their costs.

# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Principal": {
#                 "AWS": [
#                     "arn:aws:iam::${account_id}:root"
#                 ]
#             },
#             "Action": "sts:AssumeRole"
#         }
#     ]
# }

sts = boto3.client('sts')
main_account_id = sts.get_caller_identity()['Account']

# ----- STS -----
def get_session(role_arn):
    resp = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName='session'
    )
    return boto3.Session(
        aws_access_key_id=resp['Credentials']['AccessKeyId'],
        aws_secret_access_key=resp['Credentials']['SecretAccessKey'],
        aws_session_token=resp['Credentials']['SessionToken']
    )

# ----- Cost Explorer -----
def get_monthly_spend(ce, start_date=None, end_date=None):
    now = datetime.datetime.now()
    if start_date is None:
        start_date = now.strftime('%Y-%m-01')
    if end_date is None:
        if now.day == 1:
            end_date = now.strftime('%Y-%m-02')
        else:
            end_date = now.strftime('%Y-%m-%d')

    r = ce.get_cost_and_usage(
        TimePeriod={'Start': start_date, 'End': end_date},
        Granularity='MONTHLY',
        Metrics=['BlendedCost'])
    cost = r['ResultsByTime'][0]['Total']['BlendedCost']
    spend, unit = float(cost['Amount']), cost['Unit']
    return spend, unit

def get_yesterdays_spend(ce, max_items=10, threshold=0.01):
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    start_date = yesterday.strftime('%Y-%m-%d')
    end_date = now.strftime('%Y-%m-%d')

    r = ce.get_cost_and_usage(
        TimePeriod={'Start': start_date, 'End': end_date},
        Granularity='DAILY',
        Metrics=['BlendedCost'],
        GroupBy=[{
            'Type': 'DIMENSION',
            'Key': 'USAGE_TYPE'
        }])
    results = r['ResultsByTime'][0]['Groups']

    spend = []
    for x in results:
        cost = x['Keys'][0]
        amount = float(x['Metrics']['BlendedCost']['Amount'])
        if amount >= threshold:
            spend.append(
                (cost, amount)
            )
    top_spend = sorted(spend, key=lambda x: x[1], reverse=True)
    return top_spend

# ----- EC2 -----
def stop_instances(ec2):
    r = ec2.describe_instances(Filters=[{'Name':'instance-state-name','Values':['running']}])
    instance_ids_stopped = []
    for reservation in r['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            ec2.stop_instances(
                InstanceIds=[ instance_id ]
            )
            instance_ids_stopped.append(instance_id)
    return instance_ids_stopped

# ----- List Resources -----
def list_ec2_instances(region):
    ec2 = boto3.client('ec2', region_name=region)
    r = ec2.describe_instances(Filters=[{'Name':'instance-state-name','Values':['running']}])
    instances = []
    for reservation in r['Reservations']:
        for instance in reservation['Instances']:
            instances.append({
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name']
            })
    return instances

def list_sagemaker_endpoints(region):
    sagemaker = boto3.client('sagemaker', region_name=region)
    r = sagemaker.list_endpoints()
    endpoints = [{
        'EndpointName': endpoint['EndpointName'],
        'CreationTime': endpoint['CreationTime'],
        'EndpointStatus': endpoint['EndpointStatus']
    } for endpoint in r['Endpoints']]
    return endpoints

def list_resources(regions):
    for region in regions:
        txt = f"\nRegion: {region}"

        txt_ec2 = '\n- EC2 Instances:'
        instances = list_ec2_instances(region)
        if len(instances):
            for instance in instances:
                txt_ec2 += f"\n  - ID: {instance['InstanceId']}, Type: {instance['InstanceType']}, State: {instance['State']}"
        else:
            txt_ec2 = '\n- (no EC2 instances)'
        
        txt_sm = '\nSageMaker Endpoints:'
        endpoints = list_sagemaker_endpoints(region)
        if len(endpoints):
            for endpoint in endpoints:
                txt_sm += f"\n  - Name: {endpoint['EndpointName']}, Status: {endpoint['EndpointStatus']}, Created: {endpoint['CreationTime']}"
        else:
            txt_sm = '\n- (no SageMaker endpoints)'
    return txt + txt_ec2 + txt_sm

# ----- Lambda -----
def get_account_spend(account_id=None):
    if account_id is None:
        ce = boto3.client('ce')
    else:
        session = get_session(f"arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole")
        ce = session.client('ce')
    account_spend, unit = get_monthly_spend(ce)
    account_top_spend = get_yesterdays_spend(ce)
    return {
        "Monthly spend": account_spend,
        "Yesterday's spend": account_top_spend
    }

def main(args):
    account_ids = args.account_ids.split(',')

    spend = {}
    message = ''
    for account_id in account_ids:
        if account_id == main_account_id:
            spend[account_id] = get_account_spend()
        else:
            spend[account_id] = get_account_spend(account_id)
        # results['Spend'] = spend

        message += f'----- Account ID {account_id}: USD {spend[account_id]["Monthly spend"]:.2f} (Month total) -----\nYesterday\'s spend:'

        account_top_spend = spend[account_id]["Yesterday's spend"]
        for i, (item, amount) in enumerate(account_top_spend):
            message += f'\n{i+1:02d}. {item}: {amount:.2f}'
            if i == 9:
                break

    print(message)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--account_ids', type=str)
    args = parser.parse_args()
    main(args)
