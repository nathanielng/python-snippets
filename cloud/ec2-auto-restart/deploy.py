#!/usr/bin/env python3
"""
Deployment script for EC2 auto-restart Lambda function with EventBridge.
Deploys IAM role, Lambda function, and EventBridge rule.
"""
import boto3
import json
import time
import zipfile
import io

INSTANCE_ID = "i-..."
REGIONS = "us-east-1,ap-southeast-1"
FUNCTION_NAME = "ec2-start-stop"
REGION = "ap-southeast-1"
ROLE_NAME = "lambda-ec2-restart-role"

IAM_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}

iam = boto3.client('iam')
lambda_client = boto3.client('lambda', region_name=REGION)
events = boto3.client('events', region_name=REGION)
sts = boto3.client('sts')

def create_iam_role():
    print("Creating IAM role...")
    try:
        iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }]
            })
        )
    except iam.exceptions.EntityAlreadyExistsException:
        print("Role already exists")
    
    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName='ec2-restart-policy',
        PolicyDocument=json.dumps(IAM_POLICY)
    )
    
    print("Waiting for role propagation...")
    time.sleep(10)
    return iam.get_role(RoleName=ROLE_NAME)['Role']['Arn']

def create_lambda_function(role_arn):
    try:
        lambda_client.get_function(FunctionName=FUNCTION_NAME)
        print("Lambda function already exists")
        return lambda_client.get_function(FunctionName=FUNCTION_NAME)['Configuration']['FunctionArn']
    except lambda_client.exceptions.ResourceNotFoundException:
        print("Creating Lambda function...")
        with open('ec2_start_stop_lambda.py', 'rb') as f:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('ec2_start_stop_lambda.py', f.read())
            zip_buffer.seek(0)
            
            response = lambda_client.create_function(
                FunctionName=FUNCTION_NAME,
                Runtime='python3.12',
                Role=role_arn,
                Handler='ec2_start_stop_lambda.lambda_handler',
                Code={'ZipFile': zip_buffer.read()},
                Environment={'Variables': {'INSTANCE_ID': INSTANCE_ID, 'REGIONS': REGIONS}}
            )
            return response['FunctionArn']

def create_eventbridge_rule():
    print("Creating EventBridge rule...")
    events.put_rule(
        Name='ec2-restart-every-5min',
        ScheduleExpression='rate(5 minutes)',
        State='ENABLED'
    )

def add_lambda_permission(lambda_arn):
    print("Adding Lambda permission...")
    account_id = sts.get_caller_identity()['Account']
    try:
        lambda_client.add_permission(
            FunctionName=FUNCTION_NAME,
            StatementId='eventbridge-invoke',
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=f'arn:aws:events:{REGION}:{account_id}:rule/ec2-restart-every-5min'
        )
    except lambda_client.exceptions.ResourceConflictException:
        print("Permission already exists")

def add_eventbridge_target(lambda_arn):
    print("Adding target to rule...")
    events.put_targets(
        Rule='ec2-restart-every-5min',
        Targets=[{
            'Id': '1',
            'Arn': lambda_arn,
            'Input': json.dumps({'action': 'check_and_start', 'instance_id': INSTANCE_ID})
        }]
    )

def main():
    role_arn = create_iam_role()
    lambda_arn = create_lambda_function(role_arn)
    create_eventbridge_rule()
    add_lambda_permission(lambda_arn)
    add_eventbridge_target(lambda_arn)
    print("Deployment complete!")

if __name__ == '__main__':
    main()
