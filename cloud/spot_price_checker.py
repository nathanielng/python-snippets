#!/usr/bin/env python

# Example
# aws ec2 describe-spot-price-history --instance-types p5en.48xlarge --product-descriptions "Linux/UNIX" --start-time 2025-07-16T00:00:00 --end-time 2025-07-17T00:00:00 --region ap-southeast-3

import boto3
import subprocess

from datetime import datetime, timedelta
from typing import Union


def pricing_describe_services_awscli(region: str, service_code: Union[str, None] = None):
    """
    Runs the command:
    - aws pricing describe-services --region ${region}
    - aws pricing describe-services --region ${region} --service-code AmazonEC2
    """

    cmd = [
        "aws", "pricing", "describe-services",
        "--region", region
    ]
    if service_code:
        cmd.extend(["--service-code", service_code])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def get_spot_price_history_awscli(instance_type: str, region: str):
    # Get yesterday and today dates as ISO 8601 strings
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    start_time = yesterday.isoformat()
    end_time = today.isoformat()
    
    cmd = [
        "aws", "ec2", "describe-spot-price-history",
        "--instance-types", instance_type,
        "--product-descriptions", "Linux/UNIX",
        "--start-time", start_time,
        "--end-time", end_time,
        "--region", region
    ]    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def get_spot_price_history_boto3(instance_type: str, region: str = 'us-east-1'):
    ec2_client = boto3.client('ec2', region_name = region)
    response = ec2_client.describe_spot_price_history(
        InstanceTypes = [ instance_type ],
        ProductDescriptions = [ 'Linux/UNIX' ],
        StartTime = datetime.now() - timedelta(days=1),
        EndTime = datetime.now()
    )
    txt_list = []
    for price in response['SpotPriceHistory']:
        txt_list.append(
            f"{instance_type} {price['Timestamp']}: {price['SpotPrice']} ({price['AvailabilityZone']})"
        )
    return '\n'.join(txt_list)


instance_types = [
    'p5.48xlarge',
    'p5en.48xlarge'
]

regions = [
    'ap-northeast-1',
    'ap-southeast-3',
    'us-east-1',
    'us-east-2',
    'us-west-2'
]


if __name__ == "__main__":
    for region in regions:
        print(f'***** Region: {region} *****')
        for instance_type in instance_types:
            txt = get_spot_price_history_boto3(instance_type, region)
            print(txt)
