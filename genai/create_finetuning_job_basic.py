#!/usr/bin/env python

# Usage:
#   python create_finetuning_job_basic.py --train dataset.jsonl --epoch 3 --batch_size 8 --instance_type ml.g5.12xlarge

import argparse
import boto3
import datetime
import dotenv
import json
import logging
import os

from sagemaker.jumpstart.estimator import JumpStartEstimator
from sagemaker.s3 import S3Uploader


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ----- Setup Parameters -----
dotenv.load_dotenv()
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_PREFIX = os.getenv('S3_PREFIX')
MODEL_ID = os.getenv('MODEL_ID')
MODEL_VERSION = os.getenv('MODEL_VERSION')

if "AWS_DEFAULT_REGION" not in os.environ:
    os.environ["AWS_DEFAULT_REGION"] = AWS_DEFAULT_REGION

sts = boto3.client("sts")
AWS_ACCOUNT_ID = sts.get_caller_identity()["Account"]

logger.info(f'AWS_ACCOUNT_ID = {AWS_ACCOUNT_ID}')
logger.info(f'AWS_DEFAULT_REGION = {AWS_DEFAULT_REGION}')
logger.info(f'S3_BUCKET = {S3_BUCKET}')
logger.info(f'S3_PREFIX = {S3_PREFIX}')
logger.info(f'MODEL_ID = {MODEL_ID}')
logger.info(f'MODEL_VERSION = {MODEL_VERSION}')


# ----- Helper Subroutines -----
def count_lines(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    return len(lines)


# ----- Main Program -----
def main(args):

    # 0. Setup variables
    model_id = args.model_id
    model_version = args.model_version
    instance_type = args.instance_type
    region = args.region

    s3_bucket = args.s3_bucket
    s3_prefix = args.s3_prefix
    s3_location = f"s3://{s3_bucket}/{s3_prefix}"
    train_s3_location = f"{s3_location}/{args.train}"

    epoch = args.epoch
    learning_rate = args.learning_rate
    batch_size = args.batch_size
    max_input_length = args.max_input_length

    # 1. Upload to S3 bucket
    if args.skip_upload:
        logger.info("Skipping upload to S3")
    else:
        logger.info(f"Uploading the following files to: {train_s3_location}...")
        logger.info(f"- Training S3 File: {train_s3_location}")
        S3Uploader.upload(args.train, s3_location)
        logger.info("Upload complete.")
    
    # 2. Create training job metadata
    now = datetime.datetime.now()
    n = count_lines(args.train)
    logger.info(f'Number of lines of data: {n} (training)')
    job_name = f"limo-{n}-ep{epoch}-lr{learning_rate}-".replace(".", "-").replace(" ", "-") + now.strftime("%Y%m%d-%H%M")

    # 3. Prepare training job
    estimator = JumpStartEstimator(
        model_id = model_id,
        model_version = model_version,
        environment = { "accept_eula": "true" },
        disable_output_compression = True,
        instance_type = instance_type,
        region=region,
        checkpoint_s3_uri=f"s3://{s3_bucket}/checkpoints"
    )
    estimator.set_hyperparameters(
        instruction_tuned = "True",
        chat_dataset = "False",
        epoch = epoch,
        learning_rate = learning_rate,
        max_input_length = max_input_length,
        batch_size = batch_size
    )

    # 4. Log job history
    if os.path.isfile(args.job_history):
        with open(args.job_history) as f:
            job_history = json.load(f)
    else:
        job_history = []

    job_history.append({
        "job_name": job_name,
        "model_id": model_id,
        "model_version": model_version,
        "train_data": train_s3_location,
        "validation_data": "",
        "instance_type": instance_type,
        "job_data": "",
        "status": "submitted"
    })
    with open(args.job_history, "w") as f:
        json.dump(job_history, f, indent=2)

    # 5. Run training job
    print(f'***** Starting training job: `{job_name}` *****')
    print('Executing estimator.fit({')
    print('        "training": "' + str(s3_location) + '"')
    print('    },')
    print(f'    job_name={job_name}')
    print(')')
    try:
        estimator.fit(
            {
                "training": s3_location
            },
            job_name=job_name,
            wait=args.wait
        )
    except Exception as e:
        print(f'***** Exception: Training Job failed: `{job_name}` *****')
        print(e)
        raise
    
    if args.wait:
        print(f'***** Training Job submitted: `{job_name}` *****')
    else:
        print(f'***** Training Job completed: `{job_name}` *****')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--instance_type', default="ml.g5.12xlarge")
    parser.add_argument('--job_history', default="job_history.json")
    parser.add_argument('--region', default=AWS_DEFAULT_REGION)
    parser.add_argument('--s3_bucket', default=S3_BUCKET)
    parser.add_argument('--s3_prefix', default=S3_PREFIX)
    parser.add_argument('--model_id', default=MODEL_ID)
    parser.add_argument('--model_version', default=MODEL_VERSION)
    parser.add_argument('--train', required=True)
    parser.add_argument('--skip_upload', action='store_true', default=False)
    parser.add_argument('--wait', action='store_true', default=False)

    # Hyperparameters section
    parser.add_argument('--epoch', default=3, type=int)
    parser.add_argument('--learning_rate', default=1e-4, type=float)
    parser.add_argument('--batch_size', default=4, type=int)
    parser.add_argument('--max_input_length', default=1024, type=int)
    args = parser.parse_args()

    main(args)
