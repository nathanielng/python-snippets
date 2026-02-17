#!/bin/bash

# Configuration
STACK_NAME="cloudfront-s3-stack"
REGION="ap-southeast-1"
DEFAULT_TTL=0
MIN_TTL=0
MAX_TTL=0

# Generate bucket name if not provided
BUCKET_NAME=${1:-"cloudfront-s3-$(openssl rand -hex 6)"}

echo ""
echo "=== CloudFront S3 Deployment (CloudFormation) ==="
echo ""
echo "Proposed S3 bucket name: $BUCKET_NAME"
echo "Region: $REGION"
echo "Cache TTL: Min=${MIN_TTL}s, Default=${DEFAULT_TTL}s, Max=${MAX_TTL}s"
echo ""
read -p "Create this bucket? (y/n) or enter new name: " response

if [ "$response" = "n" ]; then
    echo "Deployment cancelled"
    exit 0
elif [ "$response" != "y" ]; then
    BUCKET_NAME="$response"
fi

echo ""
echo "Creating CloudFormation stack with:"
echo "  Stack Name: $STACK_NAME"
echo "  Bucket Name: $BUCKET_NAME"
echo ""
read -p "Proceed with CloudFront distribution creation? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "Creating CloudFormation stack..."

aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-body file://cloudformation-template.yaml \
  --parameters \
    ParameterKey=BucketName,ParameterValue="$BUCKET_NAME" \
    ParameterKey=DefaultTTL,ParameterValue="$DEFAULT_TTL" \
    ParameterKey=MinTTL,ParameterValue="$MIN_TTL" \
    ParameterKey=MaxTTL,ParameterValue="$MAX_TTL" \
  --region "$REGION"

if [ $? -eq 0 ]; then
    echo ""
    echo "Stack creation initiated. Waiting for completion..."
    echo "This may take 15-20 minutes..."
    echo ""
    
    aws cloudformation wait stack-create-complete \
      --stack-name "$STACK_NAME" \
      --region "$REGION"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "=== Deployment Complete ==="
        echo ""
        aws cloudformation describe-stacks \
          --stack-name "$STACK_NAME" \
          --region "$REGION" \
          --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
          --output table
    else
        echo "Stack creation failed or timed out"
        exit 1
    fi
else
    echo "Failed to create stack"
    exit 1
fi
