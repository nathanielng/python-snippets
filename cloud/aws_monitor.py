#!/usr/bin/env python

# Usage:
#   python aws_monitor.py --ec2-ls --region ap-southeast-1
#   python aws_monitor.py --ec2-start [instance_id]
#   python aws_monitor.py --ec2-stop [instance_id]
#   python aws_monitor.py --account_id [aws_account_id] --spend

# Permissions:
#   "ce:GetCostAndUsage"

import argparse
import boto3
import datetime
import json
import pandas as pd


sts = boto3.client('sts')


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
def get_monthly_spend(start_date=None, end_date=None):
    now = datetime.datetime.now()
    if start_date is None:
        start_date = now.strftime('%Y-%m-01')
    if end_date is None:
        end_date = now.strftime('%Y-%m-%d')

    r = ce.get_cost_and_usage(
        TimePeriod={'Start': start_date, 'End': end_date},
        Granularity='MONTHLY',
        Metrics=['BlendedCost'])
    cost = r['ResultsByTime'][0]['Total']['BlendedCost']
    return f"{cost['Unit']} {float(cost['Amount']):.2f}"



def get_yesterdays_spend(max_items=10):
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

    costs = []
    amounts = []
    for x in results:
        cost = x['Keys'][0]
        amount = float(x['Metrics']['BlendedCost']['Amount'])
        costs.append(cost)
        amounts.append(amount)

    df = pd.DataFrame({
        'Cost': costs,
        'Amount': amounts
    })
    new_df = df.sort_values(by='Amount', ascending=False).reset_index(drop=True)
    summary = []
    for idx, row in new_df.iterrows():
        summary.append(
            f"{idx+1}. {row['Cost']}: {row['Amount']:.2f}"
        )
    return '\n'.join(summary[:max_items])



# ----- EC2 -----
def ec2_ls():
    r = ec2.describe_instances()
    print('InstanceId,Name,InstanceType,PublicIpAddress,InstanceState')
    for reservation in r['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            instance_ip = instance.get('PublicIpAddress', '(no public ip)')

            instance_name = '(no name)'
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']

            instance_state = instance['State']['Name']
            print(f'{instance_id},{instance_name},{instance_type},{instance_ip},{instance_state}')


def ec2_stop(instance_id):
    response = ec2.stop_instances(InstanceIds=[instance_id])
    return response


def ec2_start(instance_id):
    response = ec2.start_instances(InstanceIds=[instance_id])
    return response



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--account_id', type=int, default=None, help='AWS Account ID')
    parser.add_argument('--region', type=str, default='us-east-1', help='AWS Region')
    parser.add_argument('--ec2-ls', action='store_true', help='Get list of instances')
    parser.add_argument('--ec2-stop', type=str, help='Instance Id to stop')
    parser.add_argument('--ec2-start', type=str, help='Instance Id to start')
    parser.add_argument('--spend', action='store_true', help='Retrieve monthly spend')
    parser.add_argument('--yesterday_spend', action='store_true', help='Retrieve yesterday\'s spend')
    args = parser.parse_args()


    if args.account_id is None:
        ec2 = boto3.client('ec2', region_name=args.region)
        ce = boto3.client('ce')
    else:
        role_arn = f'arn:aws:iam::{args.account_id}:role/OrganizationAccountAccessRole'
        session = get_session(role_arn)
        ec2 = session.client('ec2', region_name=args.region)
        ce = session.client('ce')


    if args.ec2_ls:
        ec2_ls()
    elif args.ec2_stop:
        response = ec2_stop(args.ec2_stop)
        print(json.dumps(response, indent=2, default=str))
    elif args.ec2_start:
        response = ec2_start(args.ec2_start)
        print(json.dumps(response, indent=2, default=str))
    elif args.spend:
        spend = get_monthly_spend()
        print(f'Monthly spend is {spend}')
    elif args.yesterday_spend:
        max_items = 10
        spend = get_yesterdays_spend(max_items)
        print(f'Yesterday\'s top {max_items} billing items are:\n{spend}')
