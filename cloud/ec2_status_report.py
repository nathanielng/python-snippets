#!/usr/bin/env python

"""
AWS Multi-Account EC2 Instance Scanner

This script scans multiple AWS accounts and regions for EC2 instances and reports their status.
It uses cross-account role assumption to access resources across different AWS accounts in an organization.

The script reads account and region mappings from a JSON configuration file and uses boto3 to:
- Assume cross-account IAM roles
- Query EC2 instances across specified accounts and regions 
- Print instance details including ID and current state

Requirements:
- AWS credentials configured with permissions to assume roles
- OrganizationAccountAccessRole available in target accounts
- Python packages: boto3, python-dotenv

Usage:
    python script.py

The account/region mappings are stored in account_region_map.json. If this file
does not exist, a default mapping will be created.
"""

import argparse
import asyncio
import boto3
import json
import os
from dotenv import load_dotenv


# Load variables from .env file or from environment
load_dotenv()


# AWS Account IDs and Regions to check for EC2 instances
# (please replace 012345678901, 123456789012 with your own Account IDs)
def write_account_region_map(json_file):
    account_regions_map = {
        '012345678901': ['us-east-1', 'us-west-2', 'ap-southeast-1'],
        '123456789012': ['us-east-1', 'us-west-2', 'ap-southeast-1']
    }
    with open(json_file, 'w') as f:
        json.dump(account_regions_map, f, indent=4)

def read_account_region_map(json_file):
    with open(json_file) as f:
        return json.load(f)

def read_or_create_account_region_map(json_file):
    if os.path.isfile(json_file):
        return read_account_region_map(json_file)
    else:
        write_account_region_map(json_file)
        return read_account_region_map(json_file)


# Setup AWS boto3 clients
sts = boto3.client('sts')
main_account_id = sts.get_caller_identity()['Account']


def get_session(role_arn):
    """
    Create an AWS session using cross-account role assumption.
    
    This function assumes a role in another AWS account and returns a boto3 session
    with temporary credentials. This enables the script to access resources across
    multiple AWS accounts in an organization.
    
    Args:
        role_arn (str): The ARN of the IAM role to assume
                       (e.g., 'arn:aws:iam::123456789012:role/OrganizationAccountAccessRole')
        
    Returns:
        boto3.Session: A boto3 session with temporary credentials for the target account
        
    Note:
        The assumed role must have the necessary permissions for the operations
        this script performs (Cost Explorer, EC2, SageMaker access).
    """
    # Assume the specified role and get temporary credentials
    resp = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName='session'  # Name for this session (appears in CloudTrail logs)
    )
    
    # Create a new boto3 session using the temporary credentials
    return boto3.Session(
        aws_access_key_id=resp['Credentials']['AccessKeyId'],
        aws_secret_access_key=resp['Credentials']['SecretAccessKey'],
        aws_session_token=resp['Credentials']['SessionToken']
    )

def get_client(account_id: str, service_name: str, region=None):
    # If target account is the same as current account, use direct access
    if account_id == main_account_id:
        if region is None:
            return boto3.client(service_name)
        else:
            return boto3.client(service_name, region_name=region)
    else:
        # For different accounts, assume the OrganizationAccountAccessRole
        # This is a standard role created by AWS Organizations for cross-account access
        session = get_session(f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole')
        if region is None:
            return session.client(service_name)
        else:
            return session.client(service_name, region_name=region)

def get_ec2_instances(account_id: str, region: str):
    ec2_client = get_client(account_id, 'ec2', region)
    response = ec2_client.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)
    return instances


async def main(args):
    """
    Main function to scan AWS accounts and regions for EC2 instances.

    This function reads account and region mappings from a JSON configuration file,
    then uses boto3 to query EC2 instances across specified accounts and regions.
    It prints instance details including ID and current state.

    Args:
        args (Namespace): Command-line arguments parsed by argparse.
                          Expected to have a 'region_map' attribute.

    Note:
        The account/region mappings are stored in account_region_map.json.
        If this file does not exist, a default mapping will be created.
    """
    account_regions_map = read_or_create_account_region_map(args.region_map)
    
    # Print table header
    print(f"{'ACCOUNT':12} {'REGION':14} {'INSTANCE ID':20} {'NAME':30} {'STATE':10}")
    print("-" * 86)
    
    for account_id in account_regions_map:
        for region in account_regions_map[account_id]:
            # get_ec2_instances is not an async function, so await is not needed
            instances = get_ec2_instances(account_id, region)
            for instance in instances:
                instance_name = ''
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            if len(instance_name) > 30:
                                instance_name = instance_name[:27] + "..."
                            break
                print(f"{account_id:12} {region:14} {instance['InstanceId']:20} {instance_name:30} {instance['State']['Name']:10}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--region-map', type=str, default='account_region_map.json')
    args = parser.parse_args()

    # Since main is async, need to use asyncio.run()
    asyncio.run(main(args))
