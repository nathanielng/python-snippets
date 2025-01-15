# Amazon SageMaker

## Setup

```bash
pip install -U sagemaker
```

## SageMaker

### JumpStart models

#### Getting the default instance type for a given `model_id`

```python
from sagemaker import instance_types
instance_type = instance_types.retrieve_default(
    model_id=model_id,
    model_version=model_version,
    scope="inference")
print(instance_type)
```

#### Deploying a JumpStart Model

```python
from sagemaker.jumpstart.model import JumpStartModel

def deploy(model_id, instance_type, **kwargs):
    model = JumpStartModel(
        model_id=model_id,
        instance_type=instance_type,
        **kwargs
    )
    predictor = model.deploy()
    return predictor, model

def predict(predictor, payload):
    response = predictor.predict(payload)
    return response[0]["generated_text"]
 
def delete_model(predictor):
    predictor.delete_model()
    predictor.delete_endpoint()

if __name__ == '__main__':
    predictor, model = deploy(
        model_id = "huggingface-...",
        instance_type = "ml.g4dn.12xlarge",
    )
    payload = {
        "inputs": "What is SageMaker JumpStart?",
        "parameters": {
            "max_new_tokens": 110,
            "no_repeat_ngram_size": 3,
        },
    }
    response = predict(predictor, payload)
    print(response)
    delete_model(predictor)
```

### Start a JumpStart Training Job

```python
import argparse
import datetime
import json

from sagemaker.jumpstart.estimator import JumpStartEstimator
from sagemaker.s3 import S3Uploader

def create_template():
    template = {
        "prompt": "{system_prompt}\n\n### Input:\n{question}",
        "completion": " {response}",
    }
    with open("template.json", "w") as f:
        json.dump(template, f)

def train(s3_location, validation_s3_location, region, epoch, learning_rate, job_name, model_id, model_version, instance_type, max_input_length="1024"):
    """
    Reference: https://sagemaker.readthedocs.io/en/stable/api/training/estimators.html
    """
    estimator = JumpStartEstimator(
        model_id = model_id,
        model_version = model_version,
        environment = { "accept_eula": "true" },
        disable_output_compression = True,
        instance_type = instance_type,
        region=region
    )
    estimator.set_hyperparameters(
        # instruction_tuned="False",
        # chat_dataset="True",
        instruction_tuned="True",
        chat_dataset="False",
        epoch=epoch,
        learning_rate=learning_rate,
        max_input_length=max_input_length
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
    region = args.region
    epoch = args.epoch
    learning_rate = args.learning_rate
    model_id = args.model_id
    model_version = args.model_version
    s3_bucket = args.s3_bucket
    s3_prefix = args.s3_prefix
    s3_location = f"s3://{s3_bucket}/{s3_prefix}"
    train_s3_location = f"{s3_location}/{args.train}"
    validation_s3_location = f"{s3_location}/{args.validation}"
    template_s3_location = f"{s3_location}/template.json"
    instance_type = args.instance_type

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
    print(f'Number of lines of data: {n} (training), {n_v} (validation)')
    job_name = f"train-ep{epoch}-lr{learning_rate}-".replace(".", "-").replace(" ", "-") + now.strftime("%Y%m%d-%H%M%S")
    print(f'Starting training job: `{job_name}`')

    try:
        response = train(
            s3_location, validation_s3_location, region, epoch, learning_rate,
            job_name, model_id, model_version, instance_type)
    except Exception as e:
        print('***** Training Job failed *****')
        print(e)
        return

    print('***** Training Job completed *****')
    print(json.dumps(response, indent=2, default=str))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws_account_id')
    parser.add_argument('--region')
    parser.add_argument('--s3_bucket')
    parser.add_argument('--s3_prefix', default="data")
    parser.add_argument('--model_id', default="meta-textgeneration-llama-3-1-70b-instruct")
    parser.add_argument('--model_version', default="2.7.0")
    parser.add_argument('--train', default='')
    parser.add_argument('--validation', default='')
    parser.add_argument('--epoch', default=3, type=int)
    parser.add_argument('--learning_rate', default=1e-4, type=float)
    parser.add_argument('--instance_type', default="ml.g5.12xlarge", type=str)
    args = parser.parse_args()
    main(args)
```


#### Retrieving a JumpStart Training Job

```python
import boto3

from sagemaker.jumpstart.estimator import JumpStartEstimator

REGION = 'us-west-2'
sagemaker_client = boto3.client('sagemaker', region_name=REGION)

def get_training_job_s3_bucket(training_job_name):
    response = sagemaker_client.describe_training_job(TrainingJobName = training_job_name)
    s3_model_artifacts = response['ModelArtifacts']['S3ModelArtifacts']
    return response['InputDataConfig'][0]['DataSource']['S3DataSource']['S3Uri']

training_job_name = '...'
model_id = '...'
s3_bucket = get_training_job_s3_bucket(training_job_name)
attached_estimator = JumpStartEstimator.attach(training_job_name, model_id)
print(attached_estimator.logs())
predictor = attached_estimator.deploy()
```


### HuggingFace models

To deploy a HuggingFace model:

```python
import boto3
improt sagemaker
from sagemaker.huggingface.model import HuggingFaceModel

try:
	# This section works inside a SageMaker environment
	sess = sagemaker.Session()
	role = sagemaker.get_execution_role()
except ValueError:
	# This section works inside a local environment
	iam = boto3.client('iam')
	role = iam.get_role(RoleName='AmazonSageMaker-ExecutionRole-...')['Role']['Arn']
	sess = sagemaker.Session()

hub = {
  'HF_MODEL_ID':'...',
  'SM_NUM_GPUS': json.dumps(1)
}

huggingface_model = HuggingFaceModel(
   # image_uri=get_huggingface_llm_image_uri("huggingface",version="1.4.0"),
   env=hub,
   role=role,
   transformers_version="4.26",
   pytorch_version="1.13",
   py_version='py39',
)

predictor = huggingface_model.deploy(
   initial_instance_count=1,
   instance_type="ml.g5.2xlarge",
   container_startup_health_check_timeout=300
)

response = predictor.predict({"inputs": "My prompt here" })
print(response)
```


## Endpoint Configurations

```python
import boto3
sm_client = boto3.client('sagemaker')

endpoint_configs = [
    config['EndpointConfigName'] for config
    in sm_client.list_endpoint_configs()['EndpointConfigs']
]
```

Delete all endpoint configurations, and associated models

```python
response = sm_client.list_endpoint_configs()
endpoint_configs = response['EndpointConfigs']
for endpoint_config in endpoint_configs:
    name = endpoint_config['EndpointConfigName']
    creation_time = endpoint_config['CreationTime']

    response = sm_client.describe_endpoint_config(EndpointConfigName=name)
    production_variant = response['ProductionVariants'][0]
    if 'ModelName' in production_variant:
        model_name = production_variant['ModelName']
    else:
        model_name = '(none)'
    instance_type = production_variant['InstanceType']
    print(f"[{creation_time}] {name}. model: {model_name}. instance: {instance_type}")

    # Delete models
    if model_name != '(none)':
        try:
            response = sm_client.delete_model(ModelName=model_name)
            print(f"- deleted model {model_name}")
        except Exception as e:
            print(f'- Error deleting model "{model_name}": {e}')

    # Delete endpoint configuration
    try:
        response = sm_client.delete_endpoint_config(EndpointConfigName=name)
        print(f"- deleted endpoint config {name}")
    except Exception as e:
        print(f'- Error deleting endpoint config "{name}": {e}')
```
