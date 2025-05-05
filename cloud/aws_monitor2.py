#!/usr/bin/env python

import argparse
import boto3
import datetime
import dotenv
import json
import logging
import os

logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv()

sts = boto3.client('sts')
main_account_id = sts.get_caller_identity()['Account']


def get_monthly_spend(ce):
    now = datetime.datetime.now(datetime.UTC)
    start_date = now.strftime('%Y-%m-01')
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
    return f"Monthly spend is: {unit} {spend:.2f}"



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
    if len(results) == 0:
        # logging.info(r)
        return 'No spend yesterday'

    spend = []
    for x in results:
        cost = x['Keys'][0]
        amount = float(x['Metrics']['BlendedCost']['Amount'])
        if amount >= threshold:
            spend.append(
                (cost, amount)
            )
    top_spend = sorted(spend, key=lambda x: x[1], reverse=True)

    txt = ''
    for i, (item, amount) in enumerate(top_spend):
        txt += f'{i+1:02d}. {item}: {amount:.2f}\n'
        if i == (max_items - 1):
            break
    return txt.strip()


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


def get_client(account_id, service_name, region=None):
    if account_id == main_account_id:
        if region is None:
            return boto3.client(service_name)
        else:
            return boto3.client(service_name, region_name=region)
    else:
        session = get_session(f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole')
        if region is None:
            return session.client(service_name)
        else:
            return session.client(service_name, region_name=region)


def get_monthly_spend_for_account_id(account_id):
    ce = get_client(account_id, 'ce')
    return get_monthly_spend(ce)


def get_yesterdays_spend_for_account_id(account_id):
    ce = get_client(account_id, 'ce')
    return get_yesterdays_spend(ce)


def print_report(account_id):
    print(f'Account ID: {account_id}')
    print(get_monthly_spend_for_account_id(account_id))
    print(get_yesterdays_spend_for_account_id(account_id))


def get_region_ec2s(ec2, filters):
    filter_list = [{'Name':'instance-state-name','Values':filters}]
    r = ec2.describe_instances(Filters=filter_list)
    instances = []
    for reservation in r['Reservations']:
        for instance in reservation['Instances']:
            instances.append({
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name']
            })
    return instances


def get_ec2s(account_id, regions, filters=['running']):
    txt = ''
    for region in regions:
        txt_region = ''
        ec2 = get_client(account_id, 'ec2', region)
        instances = get_region_ec2s(ec2, filters)
        if len(instances):
            for instance in instances:
                txt_region += f"\n  - ID: {instance['InstanceId']}, Type: {instance['InstanceType']}, State: {instance['State']}"
            txt = txt + f'\n- {region}:{txt_region}'
        else:
            txt = txt + f'\n- {region}: (no EC2 instances)'

    return 'EC2 Instances:' + txt


def get_region_sagemaker_endpoints(sagemaker, status='InService', fmt="%Y-%m-%d %H:%M%z"):
    r = sagemaker.list_endpoints(StatusEquals=status)
    endpoints = [{
        'EndpointName': endpoint['EndpointName'],
        'CreationTime': endpoint['CreationTime'].strftime(fmt),
        'EndpointStatus': endpoint['EndpointStatus']
    } for endpoint in r['Endpoints']]
    return endpoints


def get_sagemaker_eps(account_id, regions, status='InService'):
    txt = ''
    for region in regions:
        txt_region = ''
        sagemaker = get_client(account_id, 'sagemaker', region)
        endpoints = get_region_sagemaker_endpoints(sagemaker, status=status)
        if len(endpoints):
            for endpoint in endpoints:
                txt_region += f"\n  - [{endpoint['EndpointStatus']}] [{endpoint['CreationTime']}] {endpoint['EndpointName']}"
            txt = txt + f'\n- {region}:{txt_region}'
        else:
            txt = txt + f'\n- {region}: (no Sagemaker endpoints)'

    return 'Sagemaker Instances:' + txt


def main(args):
    if args.account_ids:
        account_ids = json.loads(args.account_ids)
    else:
        account_ids = {'Main': main_account_id}
    if args.region_list:
        region_list = args.region_list.split(',')
    else:
        region_list = ['us-east-1']

    for name, account_id in account_ids.items():
        print(f'----- {name} -----')
        print_report(account_id)
        print()
        print(get_ec2s(account_id, region_list))
        print()
        print(get_sagemaker_eps(account_id, region_list))
        print()


if __name__ == '__main__':    
    default_region_list = os.getenv('REGION_LIST', '')
    default_account_ids = os.getenv('ACCOUNT_ID_DATA', '')

    parser = argparse.ArgumentParser()
    parser.add_argument('--account-ids', type=str, default=default_account_ids)
    parser.add_argument('--region-list', type=str, default=default_region_list)
    args = parser.parse_args()
    main(args)
