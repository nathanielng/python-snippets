#!/usr/bin/env python
"""
AWS Resource Cleanup Tool

A utility script to clean up AWS resources including EC2 instances, S3 buckets,
SageMaker endpoints, Bedrock Knowledge Bases, and OpenSearch Serverless collections.
Supports both interactive prompting and force deletion modes.

Usage:
    python aws_cleanup.py          # Interactive mode with prompts
    python aws_cleanup.py --force  # Force deletion without prompts

Environment Variables:
    AWS_DEFAULT_REGION or AWS_REGION: AWS region for operations (required)

Requirements:
    - boto3 library
    - AWS credentials configured
    - IAM permissions for:
      * EC2: DescribeInstances, StopInstances
      * S3: ListBuckets, DeleteBucket, DeleteObject
      * SageMaker: ListEndpoints, DeleteEndpoint
      * Bedrock: ListKnowledgeBases, DeleteKnowledgeBase
      * OpenSearch Serverless: ListCollections, DeleteCollection

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

def stop_all_ec2_instances(region: str, force=False):
    """
    Stop all running EC2 instances in the specified region.
    
    Args:
        region (str): AWS region to search for instances
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Note:
        Only stops instances in 'running' state. Terminated or stopped instances are ignored.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions or service errors
    """
    ec2 = boto3.client('ec2', region_name=region)
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

def delete_all_s3_buckets(force=False):
    """
    Delete all S3 buckets and their contents (including versioned objects).
    
    Args:
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Warning:
        This operation is irreversible and will delete ALL bucket contents,
        including all object versions and delete markers.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions, bucket policies,
                    or if buckets contain objects that cannot be deleted
    """
    s3 = boto3.client('s3')
    try:
        response = s3.list_buckets()
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            if confirm_action(f"Delete S3 bucket '{bucket_name}'?", force):
                try:
                    # Delete all objects first
                    s3_resource = boto3.resource('s3')
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

def delete_all_sagemaker_endpoints(region, force=False):
    """
    Delete all SageMaker endpoints in the specified region.
    
    Args:
        region (str): AWS region to search for endpoints
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Warning:
        This will terminate all active model endpoints, stopping inference capabilities.
        Associated endpoint configurations and models are not deleted.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions or service errors
    """
    sagemaker = boto3.client('sagemaker', region_name=region)
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

def delete_all_bedrock_knowledge_bases(region, force=False):
    """
    Delete all Bedrock Knowledge Bases in the specified region.
    
    Args:
        region (str): AWS region to search for knowledge bases
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Warning:
        This will permanently delete all knowledge bases and their indexed data.
        The underlying data sources (S3 buckets, etc.) are not affected.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions or service errors
    """
    bedrock = boto3.client('bedrock-agent', region_name = region)
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

def delete_opensearch_serverless_collections(region, force=False):
    """
    Delete all OpenSearch Serverless collections in the specified region.
    
    Args:
        region (str): AWS region to search for collections
        force (bool, optional): If True, skip confirmation prompts. Defaults to False.
    
    Warning:
        This will permanently delete all collections and their data.
    
    Raises:
        ClientError: If AWS API calls fail due to permissions or service errors
    """
    aoss = boto3.client('opensearchserverless', region_name=region)
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

def cleanup_all_resources(force=False):
    """
    Execute all cleanup operations for AWS resources across multiple services.
    
    Args:
        force (bool, optional): If True, skip all confirmation prompts. Defaults to False.
    
    Note:
        Performs cleanup operations in the following order:
        1. Stop all EC2 instances
        2. Delete all S3 buckets and contents
        3. Delete all SageMaker endpoints
        4. Delete all Bedrock Knowledge Bases
        5. Delete all OpenSearch Serverless collections
        
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
    stop_all_ec2_instances(region, force)
    logger.info("Deleting S3 Buckets...")
    delete_all_s3_buckets(force)
    logger.info("Deleting SageMaker Endpoints...")
    delete_all_sagemaker_endpoints(region, force)
    logger.info("Deleting Bedrock Knowledge Bases...")
    delete_all_bedrock_knowledge_bases(region, force)
    logger.info("Deleting OpenSearch Serverless collections...")
    delete_opensearch_serverless_collections(region, force)
    logger.info("AWS resource cleanup completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AWS Resource Cleanup Tool")
    parser.add_argument("--force", action="store_true", help="Force deletion without prompting")
    args = parser.parse_args()
    
    cleanup_all_resources(args.force)
