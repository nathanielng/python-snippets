#!/usr/bin/env python

# pip3 install boto3 python-dotenv

import argparse
import boto3
import datetime
import os
import uuid

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
s3_bucket = os.getenv('S3_BUCKET')
distribution_id = os.getenv('CLOUDFRONT_DISTRIBUTION_ID')
paths_to_invalidate = os.getenv('CLOUDFRONT_PATHS_TO_INVALIDATE').split(',')


def create_cloudfront_invalidation(distribution_id, paths):
    """
    Create a CloudFront invalidation for specified paths
    
    Args:
        distribution_id (str): The CloudFront distribution ID
        paths (list): List of paths to invalidate (e.g. ['/images/*', '/css/*'])
    
    Returns:
        dict: Invalidation details if successful
    """
    try:
        # Create CloudFront client
        cloudfront_client = boto3.client('cloudfront')
        
        # Generate a unique caller reference using timestamp and UUID
        caller_reference = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())}"
        
        # Create the invalidation
        response = cloudfront_client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': caller_reference
            }
        )
        
        return response['Invalidation']
        
    except Exception as e:
        print(f"Error creating invalidation: {str(e)}")
        raise


def main(args):
    # Process arguments
    if args.distribution_id:
        distribution_id = args.distribution_id
    if args.paths:
        paths_to_invalidate = args.paths
    if args.s3_prefix:
        s3_prefix = args.s3_prefix
        s3_path = f"{s3_prefix}/{os.path.basename(args.file)}"
    else:
        s3_path = os.path.basename(args.file)

    # Upload file to S3
    if os.path.isfile(args.file):
        print(f"Uploading file to S3: {args.file}")

        try:
            s3_client = boto3.client('s3')
            s3_client.upload_file(args.file, s3_path, os.path.basename(args.file))
        except Exception as e:
            print(f"Error uploading file to S3: {str(e)}")
            raise

    # Create the CloudFront invalidation
    result = create_cloudfront_invalidation(distribution_id, paths_to_invalidate)
    print(f"Invalidation created successfully. ID: {result['Id']}")
    print(f"Status: {result['Status']}")
    print(f"Created Time: {result['CreateTime']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a CloudFront invalidation for specified paths")
    parser.add_argument("--distribution-id", default='', help="CloudFront distribution ID")
    parser.add_argument("--paths", nargs="+", default='', help="Paths to invalidate (e.g. /images/* /css/*)")
    parser.add_argument("--s3-prefix", default='', help="S3 prefix to upload file")
    parser.add_argument("--file", default='', help="File to upload to S3")
    args = parser.parse_args() 
    main(args)
