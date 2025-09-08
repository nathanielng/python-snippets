#!/usr/bin/env python

# Usage:
#   export AWS_DEFAULT_REGION="us-west-2"
#   uv run deploy_tgi.py
# Dependencies:
#   uv pip install boto3 sagemaker

import argparse
import boto3
import datetime
import logging
import os
import sagemaker
import time

from pathlib import Path
from sagemaker.model import Model
from sagemaker.s3 import S3Uploader
from sagemaker.session import Session
from sagemaker.utils import name_from_base

print(f'SageMaker version: {sagemaker.__version__}')  # 2.251.0

s3_client = boto3.client('s3')
sts = boto3.client('sts')
account_id = sts.get_caller_identity()['Account']
print(f'AWS Account ID: {account_id}')
role_arn = None


def get_execution_role_arn(role_name=None):
    if role_name is not None:
        iam = boto3.client('iam')
        return iam.get_role(RoleName=role_name)['Role']['Arn']
    try:
        role_arn = sagemaker.get_execution_role()
        # sagemaker_session  = sagemaker.Session()
    except ValueError:
        iam = boto3.client('iam')
        role_arn = iam.get_role(RoleName=role_name)['Role']['Arn']
    return role_arn

def create_config_folder(hf_model_id: str, max_model_len: int = 8192, model_loading_timeout: int = 900):
    # Create the directory that will contain the configuration files
    model_dir = Path('config')
    model_dir.mkdir(exist_ok=True)

    # Add the file `serving.properties` to the folder
    config = f"""engine=Python
    option.async_mode=true
    option.rolling_batch=disable
    option.entryPoint=djl_python.lmi_vllm.vllm_async_service
    option.tensor_parallel_degree=max
    option.model_loading_timeout={model_loading_timeout}
    fail_fast=true
    option.max_model_len={max_model_len}
    option.max_rolling_batch_size=16
    option.trust_remote_code=true
    option.model_id={hf_model_id}
    option.revision=main
    """

    with open("config/serving.properties", "w") as f:
        f.write(config)


def upload_config_folder(bucket: str, base_name: str):
    try:
        config_files_uri = S3Uploader.upload(
            local_path="config",
            desired_s3_uri=f"s3://{bucket}/lmi/{base_name}/config-files"
        )
        print(f"code_model_uri: {config_files_uri}")
        return config_files_uri
    except Exception as e:
        print(f'Exception: {e}')
    return None

def configure_model(config_files_uri, model_name, image_uri, role_arn, enable_auto_tool_choice=True, OPTION_LIMIT_MM_PER_PROMPT = None):
    """
    Example configuration:
      OPTION_LIMIT_MM_PER_PROMPT = "image=2"
    """
    model_data = {
        "S3DataSource": {
            "S3Uri": f"{config_files_uri}/",
            "S3DataType": "S3Prefix",
            "CompressionType": "None"
        }
    }
    env = {
        "HF_TASK": "Image-Text-to-Text"
    }
    if OPTION_LIMIT_MM_PER_PROMPT is not None:
        env['OPTION_LIMIT_MM_PER_PROMPT'] = OPTION_LIMIT_MM_PER_PROMPT
    if enable_auto_tool_choice:
        env['OPTIONAL_ARGS'] = "--enable-auto-tool-choice --tool-call-parser gemma"
    model = Model(
        name = model_name,
        image_uri=image_uri,
        model_data=model_data,  # Path to uncompressed code files
        role=role_arn,
        env=env
    )
    return model

def deploy_model(model, endpoint_name, gpu_instance_type):
    try:
        model.deploy(
            endpoint_name=endpoint_name,
            initial_instance_count=1,
            instance_type=gpu_instance_type,
            wait=False
        )
    except Exception as e:
        print(f"Exception: {e}")

def check_endpoint_status(endpoint_name, region_name):
    """
    Check the status of a SageMaker endpoint
    
    Parameters:
    endpoint_name (str): Name of the SageMaker endpoint
    region_name (str): AWS region name where the endpoint is deployed
    
    Returns:
    str: The current status of the endpoint
    """
    try:
        sagemaker_client = boto3.client('sagemaker', region_name=region_name)
        response = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
        endpoint_status = response['EndpointStatus']
        creation_time = response['CreationTime']
        last_modified_time = response['LastModifiedTime']       
        return endpoint_status
        
    except sagemaker_client.exceptions.ClientError as e:
        if "Could not find endpoint" in str(e):
            print(f"Endpoint {endpoint_name} does not exist.")
        else:
            print(f"Error checking endpoint status: {str(e)}")
        return None

def wait_for_endpoint(endpoint_name, region_name, timeout=1800):
    """
    Wait for the endpoint to be in service
    
    Parameters:
    endpoint_name (str): Name of the SageMaker endpoint
    region_name (str): AWS region name where the endpoint is deployed
    timeout (int): Maximum time to wait in seconds
    
    Returns:
    bool: True if endpoint is in service, False if timeout or error occurs
    """
    start_time = time.time()
    last_status = ''
    
    while time.time() - start_time < timeout:
        status = check_endpoint_status(endpoint_name, region_name)
        if status == 'InService':
            print(f"Endpoint {endpoint_name} is ready!")
            return True
        elif status in ['Failed', 'OutOfService']:
            print(f"Endpoint deployment failed with status: {status}")
            return False
        elif status in ['Creating', 'Updating']:
            if (status != last_status) or (count % 5 == 0):
                print(f"\nEndpoint status: {status}...", end='')
                count = 1
            else:
                print(".", end='', flush=True)
                count += 1
            time.sleep(10)  # Wait for 10 seconds before checking again
            last_status = status
        else:
            print(f"Unexpected status: {status}")
            return False
            
    print(f"Timeout waiting for endpoint to be ready after {timeout} seconds")
    return False

def main(args):
    now = datetime.datetime.now()

    # Step 0: Configuration
    print('Step 0: Configuration')
    region = args.region
    s3_bucket = args.s3_bucket if args.s3_bucket else f'sagemaker-{region}-{account_id}'
    image_uri = f"763104351884.dkr.ecr.{region}.amazonaws.com/djl-inference:0.33.0-lmi15.0.0-cu128"
    print(f'- Region: {region}')
    print(f'- S3 Bucket: {s3_bucket}')
    print(f'- Image URI: {image_uri}')
    role_arn = get_execution_role_arn(role_name = args.role_name)
    print(f'- RoleARN = {role_arn}')
    base_name = args.hf_model_id.split('/')[-1].replace('.', '-').lower()
    print(f"- base_name = {base_name}")
    model_lineage = args.hf_model_id.split("/")[0]
    print(f"- model_lineage = {model_lineage}")  # google
    if args.endpoint_name:
        endpoint_name = args.endpoint_name
    else:
        endpoint_name = f'{base_name}-{now.strftime("%Y%m%d-%H%M")}'
        # endpoint_name = name_from_base(base_name, short=True)
    print(f"- endpoint_name = {endpoint_name}")

    # Step 1: Create config folder & upload to S3
    print('Step 1: Creating config folder')
    create_config_folder(args.hf_model_id, args.max_model_len, args.model_loading_timeout)
    print('- Uploading to S3')
    config_files_uri = upload_config_folder(s3_bucket, base_name)
    if config_files_uri is None:
        return

    # Step 2: Configure model
    print('Step 2: Configuring model')
    model = configure_model(
        config_files_uri,
        model_name = name_from_base(base_name, short=True),
        image_uri = image_uri,
        role_arn = role_arn,
        OPTION_LIMIT_MM_PER_PROMPT = args.option_limit_mm_per_prompt
    )

    # Step 3: Deploy model to endpoint
    print(f'Step 3: Deploying model to endpoint: {endpoint_name}')
    deploy_model(model, endpoint_name, args.instance_type)
    if wait_for_endpoint(endpoint_name, region, args.model_loading_timeout+30):
        print(f"✅ Model Endpoint: {endpoint_name} has been deployed! 🚀")


if __name__ == '__main__':
    role_name = 'AmazonSageMaker-ExecutionRole-...'
    hf_model_id = '...'
    s3_bucket = 'sagemaker-...'
    option_limit_mm_per_prompt = "image=2"

    parser = argparse.ArgumentParser()
    parser.add_argument('--hf-model-id', type=str, default=hf_model_id)
    parser.add_argument('--role-name', type=str, default=role_name)
    parser.add_argument('--instance-type', type=str, default='ml.g5.12xlarge')
    parser.add_argument('--max-model-len', type=int, default=8192)
    parser.add_argument('--model-loading-timeout', type=int, default=900)
    parser.add_argument('--region', type=str, default=os.getenv('AWS_DEFAULT_REGION', 'us-west-2'))
    parser.add_argument('--s3-bucket', type=str, default=s3_bucket)
    parser.add_argument('--endpoint-name', type=str, default='')
    parser.add_argument('--option-limit-mm-per-prompt', type=str, default=option_limit_mm_per_prompt)
    args = parser.parse_args()
    main(args)
