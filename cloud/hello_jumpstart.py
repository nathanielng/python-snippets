#!/usr/bin/env python

# Example usage:
#    export AWS_DEFAULT_REGION="us-east-1"
#    python hello_jumpstart.py --list
#    python hello_jumpstart.py --predict --endpoint_name jumpstart-dft-hf-llm-llama3-8b-seal-20241122-091738
#    python hello_jumpstart.py --delete --endpoint_name jumpstart-dft-hf-llm-llama3-8b-seal-20241122-091738

# List of supported ModelIDs
# https://sagemaker.readthedocs.io/en/stable/doc_utils/pretrainedmodels.html

# Installation
# pip install sagemaker

import argparse
import boto3
import os
from sagemaker.jumpstart.model import JumpStartModel
from sagemaker.predictor import retrieve_default


model_ids = [
    "huggingface-llm-sealion-3b",
    "huggingface-llm-sealion-7b",
    "huggingface-llm-sealion-7b-instruct",
    "huggingface-llm-llama3-8b-sealionv21-instruct"
]

if 'AWS_DEFAULT_REGION' in os.environ:
    region = os.environ['AWS_DEFAULT_REGION']
else:
    region = 'us-west-2'
sagemaker_client = boto3.client('sagemaker', region_name=region)


def list_endpoints(status='InService'):
    response = sagemaker_client.list_endpoints()
    endpoint_json = response['Endpoints']
    if status.lower() == 'all':
        endpoint_ids = [ ep['EndpointName'] for ep in endpoint_json ]
    else:
        endpoint_ids = [ ep['EndpointName'] for ep in endpoint_json if ep['EndpointStatus'] == status ]
    return '\n'.join(endpoint_ids)


def deploy(model_id, instance_type, **kwargs):
    model = JumpStartModel(
        model_id=model_id,
        instance_type=instance_type,
        **kwargs
    )
    if "endpoint_name" in kwargs:
        predictor = model.deploy(
            accept_eula=True,
            endpoint_name = kwargs["endpoint_name"]
        )
    else:
        predictor = model.deploy(
            accept_eula=True
        )
    return predictor, model


def predict(predictor, payload):
    response = predictor.predict(payload)
    if isinstance(response, list):
        return response[0]["generated_text"]
    else:
        return response["generated_text"]


def delete_model(predictor):
    predictor.delete_model()
    predictor.delete_endpoint()


def main(args):
    if args.list:
        print(list_endpoints())

    if args.deploy:
        predictor, model = deploy(
            model_id = args.model_id,
            instance_type = args.instance_type,
            endpoint_name = args.endpoint_name
        )

    elif args.endpoint_name:
        # # Load the model from an existing endpoint
        # predictor = JumpStartModel(
        #     model_id=args.model_id,
        #     instance_type=args.instance_type,
        #     endpoint_name=args.endpoint_name
        # ).deploy()
        # Create a predictor from an existing endpoint
        predictor = retrieve_default(
            endpoint_name=args.endpoint_name,
            model_id=args.model_id
        )

    if args.predict:
        if args.prompt:
            prompt = args.prompt
        else:
            prompt = 'Membangun situs web dapat dilakukan dalam 10 langkah sederhana:'
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 110,
                "no_repeat_ngram_size": 3,
            },
        }   
        response = predict(predictor, payload)
        print(response)

    if args.delete:
        delete_model(predictor)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_id', type=str, default="huggingface-llm-sealion-7b-instruct")
    parser.add_argument('--instance_type', type=str, default="ml.g4dn.12xlarge")
    parser.add_argument('--endpoint_name', type=str, default=None)
    parser.add_argument('--prompt', type=str, default=None)
    parser.add_argument('--deploy', action='store_true', default=False)
    parser.add_argument('--predict', action='store_true', default=False)
    parser.add_argument('--delete', action='store_true', default=False)
    parser.add_argument('--list', action='store_true', default=False)
    args = parser.parse_args()

    main(args)
