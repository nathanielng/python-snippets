#!/usr/bin/env python

# pip3 install boto3 python-dotenv

import boto3
import datetime
import os
import uuid

from dotenv import load_dotenv

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

# Example usage
if __name__ == "__main__":
    try:
        # Load environment variables from .env file
        load_dotenv()
        distribution_id = os.getenv('CLOUDFRONT_DISTRIBUTION_ID')
        paths_to_invalidate = os.getenv('CLOUDFRONT_PATHS_TO_INVALIDATE').split(',')
        result = create_cloudfront_invalidation(distribution_id, paths_to_invalidate)
        print(f"Invalidation created successfully. ID: {result['Id']}")
        print(f"Status: {result['Status']}")
        print(f"Created Time: {result['CreateTime']}")
        
    except Exception as e:
        print(f"Failed to create invalidation: {str(e)}")
