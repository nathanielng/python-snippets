#!/usr/bin/env python

# Usage:
#   export AWS_DEFAULT_REGION="us-east-1"
#   python create_finetuning_job.py --train limo_train.jsonl --validation limo_validation.jsonl

import argparse
import datetime
import json
import os

from sagemaker import Session
from sagemaker.jumpstart.estimator import JumpStartEstimator
from sagemaker.s3 import S3Uploader



# ----- Default Parameters -----
MODEL_ID="meta-textgeneration-llama-3-2-3b-instruct"
MODEL_VERSION="1.1.0"

AWS_ACCOUNT_ID="..."
AWS_REGION="us-east-1"
S3_BUCKET=f"sagemaker-{AWS_REGION}-{AWS_ACCOUNT_ID}"
S3_PREFIX="data/nova"



# ----- Helper Subroutines -----
def count_lines(json_file):
    """
    Counts the number of lines in a JSON file.

    Args:
        json_file (str): Path to the JSON file to count lines from

    Returns:
        int: Number of lines in the file
        
    Example:
        num_lines = count_lines("data.json")
    """
    with open(json_file, "r") as f:
        lines = f.readlines()
    return len(lines)


def create_template():
    # template = {
    #     "prompt": "Below is an instruction that describes a task, paired with an input that provides further context. "
    #     "Write a response that appropriately completes the request.\n\n"
    #     "### Instruction:\n{instruction}\n\n### Input:\n{context}\n\n",
    #     "completion": " {response}",
    # }
    template = {
        "prompt": "{system_prompt}\n\n### Input:\n{question}",
        "completion": " {response}",
    }
    with open("template.json", "w") as f:
        json.dump(template, f)



def train(s3_bucket, s3_location, validation_s3_location, region, epoch, learning_rate, batch_size,
          job_name, model_id, model_version, instance_type, max_input_length="1024"):
    """
    Reference: https://sagemaker.readthedocs.io/en/stable/api/training/estimators.html
    """
    estimator = JumpStartEstimator(
        model_id = model_id,
        model_version = model_version,
        environment = { "accept_eula": "true" },
        disable_output_compression = True,
        instance_type = instance_type,
        region=region,
        checkpoint_s3_uri=f"s3://{s3_bucket}/checkpoints"
        # checkpoint_local_path='/opt/ml/checkpoints'  # default. https://docs.aws.amazon.com/sagemaker/latest/dg/model-train-storage-env-var-summary.html
        # output_path=bucket,
        # base_job_name=base_job_name,
    )
    estimator.set_hyperparameters(
        # instruction_tuned="False",
        # chat_dataset="True",
        instruction_tuned="True",
        chat_dataset="False",
        epoch=epoch,
        learning_rate=learning_rate,
        max_input_length=max_input_length,
        batch_size=batch_size
    )
    response = estimator.fit(
        {
            "training": s3_location,
            "validation": validation_s3_location
        },
        job_name=job_name
    )
    return response


def main(args):

    # 0. Setup variables
    region = args.region
    epoch = args.epoch
    learning_rate = args.learning_rate
    batch_size = args.batch_size
    instance_type = args.instance_type
    model_id = args.model_id
    model_version = args.model_version
    s3_bucket = args.s3_bucket
    s3_prefix = args.s3_prefix
    s3_location = f"s3://{s3_bucket}/{s3_prefix}"
    train_s3_location = f"{s3_location}/{args.train}"
    validation_s3_location = f"{s3_location}/{args.validation}"
    template_s3_location = f"{s3_location}/template.json"

    # 1. Upload to S3 bucket
    print(f"Uploading the following files to: {train_s3_location}...")
    print(f"- Training S3 File: {train_s3_location}")
    S3Uploader.upload(args.train, s3_location)
    print(f"- Validation S3 File: {validation_s3_location}")
    S3Uploader.upload(args.validation, s3_location)

    create_template()
    print(f"- Template S3 File: {template_s3_location}")
    S3Uploader.upload("template.json", s3_location)
    print("Upload complete.")
    
    # 2. Run training job
    now = datetime.datetime.now()
    n = count_lines(args.train)
    n_v = count_lines(args.validation)
    print(f'Number of lines of data: {n} (training), {n_v} (validation)')
    job_name = f"train-{n}-ep{epoch}-lr{learning_rate}-".replace(".", "-").replace(" ", "-") + now.strftime("%Y%m%d-%H%M%S")
    print(f'Starting training job: `{job_name}`')

    try:
        response = train(
            s3_bucket, s3_location, validation_s3_location, region, epoch, learning_rate, batch_size,
            job_name, model_id, model_version, instance_type)
    except Exception as e:
        print('***** Training Job failed *****')
        print(e)
        return

    print('***** Training Job completed *****')
    print(json.dumps(response, indent=2, default=str))

    # 3. Load job history
    if os.path.isfile(args.job_history):
        with open(args.job_history) as f:
            job_history = json.load(f)
    else:
        job_history = []

    # 4. Save job history
    job_history.append({
        "job_name": job_name,
        "model_id": model_id,
        "model_version": model_version,
        "train_data": train_s3_location,
        "validation_data": validation_s3_location,
        "instance_type": instance_type,
        "job_data": response
    })
    with open(args.job_history, "w") as f:
        json.dump(job_history, f, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws_account_id', default=AWS_ACCOUNT_ID)
    parser.add_argument('--instance_type', default="ml.g5.12xlarge")
    parser.add_argument('--job_history', default="job_history.json")
    parser.add_argument('--region', default=AWS_REGION)
    parser.add_argument('--s3_bucket', default=S3_BUCKET)
    parser.add_argument('--s3_prefix', default=S3_PREFIX)
    parser.add_argument('--model_id', default=MODEL_ID)
    parser.add_argument('--model_version', default=MODEL_VERSION)
    parser.add_argument('--train', default='')
    parser.add_argument('--validation', default='')

    # Hyperparameters section
    parser.add_argument('--epoch', default=3, type=int)
    parser.add_argument('--learning_rate', default=1e-4, type=float)
    parser.add_argument('--batch_size', default=4, type=int)
    args = parser.parse_args()

    main(args)
