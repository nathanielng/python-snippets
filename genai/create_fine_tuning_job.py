import argparse
import json
import os
import sagemaker

from sagemaker.jumpstart.model import JumpStartModel
from sagemaker.jumpstart.estimator import JumpStartEstimator
from sagemaker.s3 import S3Uploader



model_id, model_version = "meta-textgeneration-llama-3-8b-instruct", "2.3.0"

AWS_ACCOUNT_ID = os.getenv('AWS_ACCOUNT_ID')
REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
if REGION in ['us-east-1', 'us-west-2', 'ap-southeast-1']:
    S3_BUCKET = f"sagemaker-{REGION}-{AWS_ACCOUNT_ID}"
else:
    S3_BUCKET = sagemaker.Session().default_bucket()



def deploy_pretrained_model():
    pretrained_model = JumpStartModel(model_id=model_id, model_version=model_version)
    pretrained_predictor = pretrained_model.deploy(accept_eula=True)



def create_template():
    template = {
        "prompt": "Below is an instruction that describes a task, paired with an input that provides further context. "
        "Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Input:\n{context}\n\n",
        "completion": " {response}",
    }
    with open("template.json", "w") as f:
        json.dump(template, f)



def train(train_data_location):
    estimator = JumpStartEstimator(
        model_id=model_id,
        model_version=model_version,
        environment={"accept_eula": "true"},
        disable_output_compression=True,
        instance_type="ml.g5.12xlarge",   # For Llama-3-70b, use "ml.g5.48xlarge"
        region=REGION
    )
    estimator.set_hyperparameters(
        instruction_tuned="True",  # Default is false
        chat_dataset="False",
        epoch="1",
        # max_input_length="1024"
    )
    response = estimator.fit({"training": train_data_location})
    return response



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('--s3_bucket', default=S3_BUCKET)
    args = parser.parse_args()

    train_s3_folder = f"s3://{S3_BUCKET}/train/lol"
    train_s3_location = f"s3://{S3_BUCKET}/train/lol/{args.file}"
    # S3Uploader.upload("template.json", train_data_location)
    S3Uploader.upload(args.file, train_s3_folder)
    print(f"Training S3 Folder: {train_s3_folder}")
    print(f"Training S3 Location: {train_s3_location}")
    
    response = train(train_s3_location)
    print('***** Training Job completed *****')
    print(json.dumps(response, indent=2, default=str))
