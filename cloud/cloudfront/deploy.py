#!/usr/bin/env python3
"""
Deployment script for CloudFront distribution with S3 origin.

Creates:
- S3 bucket (with user confirmation and optional rename)
- Origin Access Control (OAC) for secure CloudFront-to-S3 access
- CloudFront distribution with configurable TTL
- Bucket policy allowing CloudFront access only

Configuration:
- BUCKET_NAME: S3 bucket name (None = auto-generate)
- REGION: AWS region for S3 bucket
- DISTRIBUTION_COMMENT: CloudFront distribution description
- DEFAULT_TTL, MIN_TTL, MAX_TTL: Cache TTL in seconds (default: 0 = no cache)

Usage:
    python3 deploy.py

The script prompts for confirmation before creating resources.
"""
import boto3
import json
import time
import uuid

# Configuration
BUCKET_NAME = None  # Set to None to auto-generate, or specify bucket name
REGION = "us-east-1"
DISTRIBUTION_COMMENT = "S3 CloudFront Distribution"
DEFAULT_TTL = 0  # Default cache TTL in seconds (0 = no cache)
MIN_TTL = 0  # Minimum cache TTL in seconds
MAX_TTL = 0  # Maximum cache TTL in seconds

s3 = boto3.client('s3', region_name=REGION)
cloudfront = boto3.client('cloudfront')

def create_s3_bucket(bucket_name):
    """Create S3 bucket if it doesn't exist."""
    print(f"\nProposed S3 bucket name: {bucket_name}")
    response = input("Create this bucket? (y/n) or enter new name: ").strip()
    
    if response.lower() == 'n':
        print("Deployment cancelled")
        exit(0)
    elif response.lower() != 'y':
        bucket_name = response
    
    print(f"Creating S3 bucket: {bucket_name}")
    try:
        if REGION == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': REGION}
            )
        print(f"Bucket {bucket_name} created")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket {bucket_name} already exists")
    except s3.exceptions.BucketAlreadyExists:
        print(f"Bucket {bucket_name} already exists (owned by someone else)")
        raise
    
    # Block public access
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
    return bucket_name

def create_oac():
    """Create Origin Access Control for CloudFront."""
    print("Creating Origin Access Control...")
    oac_config = {
        'Name': f'OAC-{uuid.uuid4().hex[:8]}',
        'Description': 'OAC for S3 bucket access',
        'SigningProtocol': 'sigv4',
        'SigningBehavior': 'always',
        'OriginAccessControlOriginType': 's3'
    }
    
    response = cloudfront.create_origin_access_control(
        OriginAccessControlConfig=oac_config
    )
    return response['OriginAccessControl']['Id']

def create_cloudfront_distribution(bucket_name, oac_id):
    """Create CloudFront distribution with S3 origin."""
    print(f"\nReady to create CloudFront distribution for bucket: {bucket_name}")
    print(f"Cache TTL: Min={MIN_TTL}s, Default={DEFAULT_TTL}s, Max={MAX_TTL}s")
    response = input("Create CloudFront distribution? (y/n): ").strip()
    
    if response.lower() != 'y':
        print("Deployment cancelled")
        exit(0)
    
    print("Creating CloudFront distribution...")
    
    distribution_config = {
        'CallerReference': str(uuid.uuid4()),
        'Comment': DISTRIBUTION_COMMENT,
        'Enabled': True,
        'Origins': {
            'Quantity': 1,
            'Items': [{
                'Id': f's3-{bucket_name}',
                'DomainName': f'{bucket_name}.s3.{REGION}.amazonaws.com',
                'OriginAccessControlId': oac_id,
                'S3OriginConfig': {'OriginAccessIdentity': ''}
            }]
        },
        'DefaultCacheBehavior': {
            'TargetOriginId': f's3-{bucket_name}',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {
                'Quantity': 2,
                'Items': ['GET', 'HEAD'],
                'CachedMethods': {'Quantity': 2, 'Items': ['GET', 'HEAD']}
            },
            'Compress': True,
            'MinTTL': MIN_TTL,
            'DefaultTTL': DEFAULT_TTL,
            'MaxTTL': MAX_TTL,
            'ForwardedValues': {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            },
            'TrustedSigners': {'Enabled': False, 'Quantity': 0}
        },
        'DefaultRootObject': 'index.html'
    }
    
    response = cloudfront.create_distribution(DistributionConfig=distribution_config)
    distribution_id = response['Distribution']['Id']
    domain_name = response['Distribution']['DomainName']
    arn = response['Distribution']['ARN']
    
    return distribution_id, domain_name, arn

def update_bucket_policy(bucket_name, distribution_arn):
    """Add bucket policy to allow CloudFront access."""
    print("Updating S3 bucket policy...")
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "AllowCloudFrontServicePrincipal",
            "Effect": "Allow",
            "Principal": {"Service": "cloudfront.amazonaws.com"},
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/*",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceArn": distribution_arn
                }
            }
        }]
    }
    
    s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))

def main():
    bucket_name = BUCKET_NAME or f'cloudfront-s3-{uuid.uuid4().hex[:12]}'
    
    bucket_name = create_s3_bucket(bucket_name)
    oac_id = create_oac()
    distribution_id, domain_name, arn = create_cloudfront_distribution(bucket_name, oac_id)
    update_bucket_policy(bucket_name, arn)
    
    print("\n=== Deployment Complete ===")
    print(f"S3 Bucket: {bucket_name}")
    print(f"CloudFront Distribution ID: {distribution_id}")
    print(f"CloudFront Domain: {domain_name}")
    print(f"CloudFront URL: https://{domain_name}")
    print("\nNote: Distribution deployment takes 15-20 minutes to complete.")

if __name__ == '__main__':
    main()
