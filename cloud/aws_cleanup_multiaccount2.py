#!/usr/bin/env python
"""
AWS Resource Cleanup Tool

A utility script to clean up AWS resources including EC2 instances, S3 buckets,
SageMaker endpoints, Bedrock Knowledge Bases, and OpenSearch Serverless collections.
Supports both interactive prompting and force deletion modes with cross-account access.

Usage:
    python aws_cleanup.py                           # Interactive mode with prompts
    python aws_cleanup.py --force                   # Force deletion without prompts
    python aws_cleanup.py --s3                      # Include S3 bucket cleanup
    python aws_cleanup.py --terminate-ec2           # Terminate EC2 instances instead of stopping them
    python aws_cleanup.py --account_id 123456789012 # Target specific account

Requirements:
    - boto3 library
    - AWS credentials configured
    - IAM permissions for:
      * EC2: DescribeInstances, StopInstances
      * S3: ListBuckets, DeleteBucket, DeleteObject
      * SageMaker: ListEndpoints, DeleteEndpoint, ListDomains, DeleteDomain, ListUserProfiles, DeleteUserProfile, ListApps, DeleteApp, ListSpaces, DeleteSpace
      * Bedrock: ListKnowledgeBases, DeleteKnowledgeBase
      * OpenSearch Serverless: ListCollections, DeleteCollection
      * STS: AssumeRole (for cross-account access)

To specify the target AWS Account ID & region, export the following before running this script
    export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    export AWS_DEFAULT_REGION="..."

Warning:
    This tool performs destructive operations that cannot be undone.
    Use with extreme caution, especially in production environments.
"""

import argparse
import boto3
import logging
import os
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
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
    except ClientError as e:
        logger.error(f"Failed to assume role {role_arn}: {e}")
        raise

def get_session_keys(role_arn):
    try:
        resp = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName='session'  # Name for this session (appears in CloudTrail logs)
        )
        return {
            'aws_access_key_id': resp['Credentials']['AccessKeyId'],
            'aws_secret_access_key': resp['Credentials']['SecretAccessKey'],
            'aws_session_token': resp['Credentials']['SessionToken']
        }
    except ClientError as e:
        logger.error(f"Failed to assume role {role_arn}: {e}")
        raise

def get_resource(account_id, resource, region=None):
    try:
        resp = sts.assume_role(
            RoleArn=f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole',
            RoleSessionName='session'  # Name for this session (appears in CloudTrail logs)
        )
        return boto3.resource(
            service_name=resource,
            region_name=region,
            aws_access_key_id=resp['Credentials']['AccessKeyId'],
            aws_secret_access_key=resp['Credentials']['SecretAccessKey'],
            aws_session_token=resp['Credentials']['SessionToken']
        )
    except ClientError as e:
        logger.error(f"Failed to assume role for account {account_id}: {e}")
        raise

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

def confirm_action(message, force=False):
    """
    Prompt user for yes/no confirmation.
    
    Args:
        message (str): Confirmation message to display
        force (bool): If True, skip prompting and return True
    
    Returns:
        bool: True if confirmed or forced, False otherwise
    """
    if force:
        return True
    response = input(f"{message} (y/N): ").strip().lower()
    return response in ['y', 'yes']

def stop_all_ec2_instances(account_id, region: str, force=False):
    """
    Stop all running EC2 instances in the current region.
    
    Args:
        force (bool): If True, skip confirmation prompts
    
    Raises:
        ClientError: If AWS API calls fail
    """
    ec2 = get_client(account_id, 'ec2', region=region)
    try:
        response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])
        
        if instance_ids:
            for instance_id in instance_ids:
                if confirm_action(f"Stop EC2 instance {instance_id}?", force):
                    ec2.stop_instances(InstanceIds=[instance_id])
                    logger.info(f"Stopped EC2 instance: {instance_id}")
                else:
                    logger.info(f"Skipped stopping EC2 instance: {instance_id}")
        else:
            logger.info("No running EC2 instances found")

    except ClientError as e:
        logger.error(f"Error stopping EC2 instances: {e}")

def terminate_all_ec2_instances(account_id, region: str, force=False):
    """
    Terminate all EC2 instances in the current region.

    Args:
        force (bool): If True, skip confirmation prompts

    Raises:
        ClientError: If AWS API calls fail
    """
    ec2 = get_client(account_id, 'ec2', region=region)
    try:
        response = ec2.describe_instances()
        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])

        if instance_ids:
            for instance_id in instance_ids:
                if confirm_action(f"Terminate EC2 instance {instance_id}?", force):
                    ec2.terminate_instances(InstanceIds=[instance_id])
                    logger.info(f"Terminated EC2 instance: {instance_id}")
                else:
                    logger.info(f"Skipped terminating EC2 instance: {instance_id}")
        else:
            logger.info("No EC2 instances found")

    except ClientError as e:
        logger.error(f"Error terminating EC2 instances: {e}")

def delete_all_s3_buckets(account_id, force=False):
    """
    Delete all S3 buckets and their contents (including versioned objects).
    
    Args:
        force (bool): If True, skip confirmation prompts
    
    Note:
        This operation is irreversible and will delete ALL bucket contents
    
    Raises:
        ClientError: If AWS API calls fail
    """
    s3 = get_client(account_id, 's3')
    s3_resource = get_resource(account_id, 's3')
    try:
        response = s3.list_buckets()
        buckets_to_delete = []
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            if confirm_action(f"Delete S3 bucket '{bucket_name}'?", force):
                buckets_to_delete.append(bucket_name)
            else:
                logger.info(f"Skipped deleting S3 bucket: {bucket_name}")
        
        for bucket_name in buckets_to_delete:
            try:
                bucket_resource = s3_resource.Bucket(bucket_name)
                bucket_resource.object_versions.delete()
                # Delete bucket
                s3.delete_bucket(Bucket=bucket_name)
                logger.info(f"Deleted S3 bucket: {bucket_name}")
            except ClientError as e:
                logger.error(f"Error deleting bucket {bucket_name}: {e}")
    except ClientError as e:
        logger.error(f"Error listing S3 buckets: {e}")

def delete_all_sagemaker_endpoints(account_id, region, force=False):
    """
    Delete all SageMaker endpoints in the current region.
    
    Args:
        force (bool): If True, skip confirmation prompts
    
    Note:
        This will terminate all active model endpoints
    
    Raises:
        ClientError: If AWS API calls fail
    """
    sagemaker = get_client(account_id, 'sagemaker', region=region)
    try:
        response = sagemaker.list_endpoints()
        endpoints_to_delete = []
        for endpoint in response['Endpoints']:
            endpoint_name = endpoint['EndpointName']
            if confirm_action(f"Delete SageMaker endpoint '{endpoint_name}'?", force):
                endpoints_to_delete.append(endpoint_name)
            else:
                logger.info(f"Skipped deleting SageMaker endpoint: {endpoint_name}")
        
        for endpoint_name in endpoints_to_delete:
            try:
                sagemaker.delete_endpoint(EndpointName=endpoint_name)
                logger.info(f"Deleted SageMaker endpoint: {endpoint_name}")
            except ClientError as e:
                logger.error(f"Error deleting endpoint {endpoint_name}: {e}")
    except ClientError as e:
        logger.error(f"Error listing SageMaker endpoints: {e}")

def delete_all_bedrock_knowledge_bases(account_id, region, force=False):
    """
    Delete all Bedrock Knowledge Bases in the current region.
    
    Args:
        force (bool): If True, skip confirmation prompts
    
    Note:
        This will permanently delete all knowledge bases and their data
    
    Raises:
        ClientError: If AWS API calls fail
    """
    bedrock = get_client(account_id, 'bedrock-agent', region=region)
    try:
        response = bedrock.list_knowledge_bases()
        for kb in response['knowledgeBaseSummaries']:
            kb_id = kb['knowledgeBaseId']
            kb_name = kb.get('name', kb_id)
            if confirm_action(f"Delete Bedrock Knowledge Base '{kb_name}' ({kb_id})?", force):
                try:
                    bedrock.delete_knowledge_base(knowledgeBaseId=kb_id)
                    logger.info(f"Deleted Bedrock Knowledge Base: {kb_id}")
                except ClientError as e:
                    logger.error(f"Error deleting Knowledge Base {kb_id}: {e}")
            else:
                logger.info(f"Skipped deleting Bedrock Knowledge Base: {kb_id}")
    except ClientError as e:
        logger.error(f"Error listing Bedrock Knowledge Bases: {e}")

def delete_opensearch_serverless_collections(account_id, region, force=False):
    """
    Delete all OpenSearch Serverless collections in the current region.
    
    Args:
        account_id (str): AWS Account ID
        region (str): AWS region
        force (bool): If True, skip confirmation prompts
    
    Note:
        This will permanently delete all collections and their data
    
    Raises:
        ClientError: If AWS API calls fail
    """
    aoss = get_client(account_id, 'opensearchserverless', region=region)
    try:
        response = aoss.list_collections()
        for collection in response['collectionSummaries']:
            collection_id = collection['id']
            collection_name = collection['name']
            if confirm_action(f"Delete OpenSearch Serverless collection '{collection_name}' ({collection_id})?", force):
                try:
                    aoss.delete_collection(id=collection_id)
                    logger.info(f"Deleted OpenSearch Serverless collection: {collection_name} ({collection_id})")
                except ClientError as e:
                    logger.error(f"Error deleting collection {collection_name}: {e}")
            else:
                logger.info(f"Skipped deleting OpenSearch Serverless collection: {collection_name}")
    except ClientError as e:
        logger.error(f"Error listing OpenSearch Serverless collections: {e}")

def cleanup_all_resources(account_id, args):
    """
    Execute all cleanup operations for AWS resources.
    
    Args:
        force (bool): If True, skip all confirmation prompts
    
    Note:
        Runs cleanup for EC2, S3, SageMaker, and Bedrock resources
    """
    force = args.force
    logger.info(f"Starting AWS resource cleanup... (force={force})")

    region = os.getenv('AWS_DEFAULT_REGION', os.getenv('AWS_REGION', ''))
    if not region:
        print('No AWS region specified. Please set the environment variable AWS_DEFAULT_REGION')
        return
    logger.info(f"Using AWS region: {region}")

    logger.info("Stopping EC2 Instances...")
    stop_all_ec2_instances(account_id, region, force)
    logger.info("Deleting SageMaker Endpoints...")
    delete_all_sagemaker_endpoints(account_id, region, force)
    logger.info("Deleting Bedrock Knowledge Bases...")
    delete_all_bedrock_knowledge_bases(account_id, region, force)
    logger.info("Deleting OpenSearch Serverless collections...")
    delete_opensearch_serverless_collections(account_id, region, force)
    if args.terminate_ec2:
        logger.info("Terminating EC2 Instances...")
        terminate_all_ec2_instances(account_id, region, force)
    if args.s3:
        logger.info("Deleting S3 Buckets...")
        delete_all_s3_buckets(account_id, force)
    logger.info("AWS resource cleanup completed")

try:
    sts = boto3.client('sts')
    main_account_id = sts.get_caller_identity()["Account"]
    logger.info(f'Using AWS Account ID: {main_account_id}')
except ClientError as e:
    logger.error(f"Failed to get AWS caller identity: {e}")
    logger.error("Please check your AWS credentials and permissions")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error getting AWS caller identity: {e}")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AWS Resource Cleanup Tool")
    parser.add_argument("--force", action="store_true", help="Force deletion without prompting")
    parser.add_argument("--s3", action="store_true", help="Cleanup S3 buckets")
    parser.add_argument("--terminate-ec2", action="store_true", help="Terminate EC2 instances")
    parser.add_argument("--account_id", default=os.getenv('AWS_ACCOUNT_ID', main_account_id))
    args = parser.parse_args()
    
    cleanup_all_resources(args.account_id, args)
