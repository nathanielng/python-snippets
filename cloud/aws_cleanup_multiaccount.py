#!/usr/bin/env python
"""
AWS Resource Cleanup Tool

A utility script to clean up AWS resources including EC2 instances, S3 buckets,
SageMaker endpoints, Bedrock Knowledge Bases, and OpenSearch Serverless collections.
Supports both interactive prompting and force deletion modes with cross-account access.

Usage:
    python aws_cleanup.py                           # Interactive mode with prompts
    python aws_cleanup.py --force                   # Force deletion without prompts
    python aws_cleanup.py --account_id 123456789012 # Target specific account

Environment Variables:
    AWS_ACCOUNT_ID: Target AWS account ID (optional, defaults to current account)
    AWS_DEFAULT_REGION or AWS_REGION: AWS region for operations (required)

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
        this script performs (EC2, S3, SageMaker, Bedrock, OpenSearch Serverless access).
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

def get_session_keys(role_arn):
    """
    Get temporary AWS credentials by assuming a cross-account role.
    
    Args:
        role_arn (str): The ARN of the IAM role to assume
                       (e.g., 'arn:aws:iam::123456789012:role/OrganizationAccountAccessRole')
        
    Returns:
        dict: Dictionary containing temporary AWS credentials with keys:
              - aws_access_key_id (str): Temporary access key ID
              - aws_secret_access_key (str): Temporary secret access key
              - aws_session_token (str): Temporary session token
              
    Raises:
        ClientError: If role assumption fails due to permissions or invalid role ARN
    """
    resp = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName='session'  # Name for this session (appears in CloudTrail logs)
    )
    return {
        'aws_access_key_id': resp['Credentials']['AccessKeyId'],
        'aws_secret_access_key': resp['Credentials']['SecretAccessKey'],
        'aws_session_token': resp['Credentials']['SessionToken']
    }

def get_resource(account_id, resource, region=None):
    """
    Create a boto3 resource for a specific AWS service in a target account.
    
    Args:
        account_id (str): Target AWS account ID
        resource (str): AWS service name (e.g., 's3', 'ec2', 'dynamodb')
        region (str, optional): AWS region name. Defaults to None.
        
    Returns:
        boto3.resource: A boto3 resource object for the specified service
        
    Raises:
        ClientError: If role assumption fails or service is not available
    """
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

def get_client(account_id: str, service_name: str, region=None):
    """
    Create a boto3 client for a specific AWS service, supporting cross-account access.
    
    Args:
        account_id (str): Target AWS account ID
        service_name (str): AWS service name (e.g., 'ec2', 's3', 'sagemaker')
        region (str, optional): AWS region name. Defaults to None.
        
    Returns:
        boto3.client: A boto3 client object for the specified service
        
    Note:
        If the target account matches the current account, uses direct access.
        Otherwise, assumes the OrganizationAccountAccessRole for cross-account access.
        
    Raises:
        ClientError: If role assumption fails or service is not available
    """
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
    Stop all running EC2 instances in the specified region.
    
    Args:
        account_id (str): AWS account ID containing the instances
        region (str): AWS region to search for instances
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Note:
        Only stops instances in 'running' state. Terminated or stopped instances are ignored.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions or service errors
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

def delete_all_s3_buckets(account_id, force=False):
    """
    Delete all S3 buckets and their contents (including versioned objects).
    
    Args:
        account_id (str): AWS account ID containing the S3 buckets
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Warning:
        This operation is irreversible and will delete ALL bucket contents,
        including all object versions and delete markers.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions, bucket policies,
                    or if buckets contain objects that cannot be deleted
    """
    s3 = get_client(account_id, 's3')
    try:
        response = s3.list_buckets()
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            if confirm_action(f"Delete S3 bucket '{bucket_name}'?", force):
                try:
                    s3_resource = get_resource(account_id, 's3')
                    bucket_resource = s3_resource.Bucket(bucket_name)
                    bucket_resource.objects.all().delete()
                    bucket_resource.object_versions.all().delete()
                    
                    # Delete bucket
                    s3.delete_bucket(Bucket=bucket_name)
                    logger.info(f"Deleted S3 bucket: {bucket_name}")
                except ClientError as e:
                    logger.error(f"Error deleting bucket {bucket_name}: {e}")
            else:
                logger.info(f"Skipped deleting S3 bucket: {bucket_name}")
    except ClientError as e:
        logger.error(f"Error listing S3 buckets: {e}")

def delete_all_sagemaker_endpoints(account_id, region, force=False):
    """
    Delete all SageMaker endpoints in the specified region.
    
    Args:
        account_id (str): AWS account ID containing the SageMaker endpoints
        region (str): AWS region to search for endpoints
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Warning:
        This will terminate all active model endpoints, stopping inference capabilities.
        Associated endpoint configurations and models are not deleted.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions or service errors
    """
    sagemaker = get_client(account_id, 'sagemaker', region=region)
    try:
        response = sagemaker.list_endpoints()
        for endpoint in response['Endpoints']:
            endpoint_name = endpoint['EndpointName']
            if confirm_action(f"Delete SageMaker endpoint '{endpoint_name}'?", force):
                try:
                    sagemaker.delete_endpoint(EndpointName=endpoint_name)
                    logger.info(f"Deleted SageMaker endpoint: {endpoint_name}")
                except ClientError as e:
                    logger.error(f"Error deleting endpoint {endpoint_name}: {e}")
            else:
                logger.info(f"Skipped deleting SageMaker endpoint: {endpoint_name}")
    except ClientError as e:
        logger.error(f"Error listing SageMaker endpoints: {e}")

def delete_all_bedrock_knowledge_bases(account_id, region, force=False):
    """
    Delete all Bedrock Knowledge Bases in the specified region.
    
    Args:
        account_id (str): AWS account ID containing the Bedrock Knowledge Bases
        region (str): AWS region to search for knowledge bases
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Warning:
        This will permanently delete all knowledge bases and their indexed data.
        The underlying data sources (S3 buckets, etc.) are not affected.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions or service errors
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

def delete_all_sagemaker_domains(account_id, region, force=False):
    """
    Delete all SageMaker domains in the specified region.
    
    Args:
        account_id (str): AWS account ID containing the SageMaker domains
        region (str): AWS region to search for domains
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Warning:
        This will permanently delete all SageMaker domains and associated user profiles.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions or service errors
    """
    sagemaker = get_client(account_id, 'sagemaker', region=region)
    try:
        response = sagemaker.list_domains()
        for domain in response['Domains']:
            domain_id = domain['DomainId']
            domain_name = domain['DomainName']
            if confirm_action(f"Delete SageMaker domain '{domain_name}' ({domain_id})?", force):
                try:
                    # Delete all apps and spaces in user profiles first
                    user_profiles = sagemaker.list_user_profiles(DomainIdEquals=domain_id)
                    for profile in user_profiles['UserProfiles']:
                        profile_name = profile['UserProfileName']
                        # Delete apps
                        apps = sagemaker.list_apps(DomainIdEquals=domain_id, UserProfileNameEquals=profile_name)
                        for app in apps['Apps']:
                            sagemaker.delete_app(DomainId=domain_id, UserProfileName=profile_name, AppType=app['AppType'], AppName=app['AppName'])
                            logger.info(f'Deleted app: {app["AppName"]}')

                        # Delete spaces
                        spaces = sagemaker.list_spaces(DomainIdEquals=domain_id)
                        for space in spaces['Spaces']:
                            if space.get('OwnershipSettings', {}).get('OwnerUserProfileName') == profile_name:
                                sagemaker.delete_space(DomainId=domain_id, SpaceName=space['SpaceName'])
                                logger.info(f'Deleted space: {space["SpaceName"]}')

                        sagemaker.delete_user_profile(DomainId=domain_id, UserProfileName=profile_name)
                        logger.info(f'Deleted user profile: {profile_name}')
                    
                    sagemaker.delete_domain(DomainId=domain_id)
                    logger.info(f"Deleted SageMaker domain: {domain_name} ({domain_id})")
                except ClientError as e:
                    logger.error(f"Error deleting domain {domain_name}: {e}")
            else:
                logger.info(f"Skipped deleting SageMaker domain: {domain_name}")
    except ClientError as e:
        logger.error(f"Error listing SageMaker domains: {e}")

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

def cleanup_all_resources(account_id, force=False):
    """
    Execute all cleanup operations for AWS resources across multiple services.
    
    Args:
        account_id (str): AWS account ID to clean up resources in
        force (bool, optional): If True, skip all confirmation prompts. Defaults to False.
    
    Note:
        Performs cleanup operations in the following order:
        1. Stop all EC2 instances
        2. Delete all S3 buckets and contents
        3. Delete all SageMaker endpoints
        4. Delete all SageMaker domains
        5. Delete all Bedrock Knowledge Bases
        6. Delete all OpenSearch Serverless collections
        
        Requires AWS_DEFAULT_REGION or AWS_REGION environment variable to be set.
    
    Warning:
        All operations are destructive and irreversible. Ensure you have
        proper backups before running this script.
    """
    logger.info("Starting AWS resource cleanup...")

    region = os.getenv('AWS_DEFAULT_REGION', os.getenv('AWS_REGION', ''))
    if not region:
        print('No AWS region specified. Please set the environment variable AWS_DEFAULT_REGION')
        return
    logger.info(f"Using AWS region: {region}")

    logger.info("Stopping EC2 Instances...")
    stop_all_ec2_instances(account_id, region, force)
    logger.info("Deleting S3 Buckets...")
    delete_all_s3_buckets(account_id, force)
    logger.info("Deleting SageMaker Endpoints...")
    delete_all_sagemaker_endpoints(account_id, region, force)
    logger.info("Deleting SageMaker Domains...")
    delete_all_sagemaker_domains(account_id, region, force)
    logger.info("Deleting Bedrock Knowledge Bases...")
    delete_all_bedrock_knowledge_bases(account_id, region, force)
    logger.info("Deleting OpenSearch Serverless collections...")
    delete_opensearch_serverless_collections(account_id, region, force)
    logger.info("AWS resource cleanup completed")

sts = boto3.client('sts')
main_account_id = sts.get_caller_identity()["Account"]
logger.info(f'Using AWS Account ID: {main_account_id}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AWS Resource Cleanup Tool")
    parser.add_argument("--force", action="store_true", help="Force deletion without prompting")
    parser.add_argument("--account_id", default=os.getenv('AWS_ACCOUNT_ID', main_account_id))
    args = parser.parse_args()
    
    cleanup_all_resources(args.account_id, args.force)
