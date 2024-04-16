# Amazon SageMaker

## Setup

```bash
pip install -U sagemaker
```

## SageMaker

### JumpStart models

Getting the default instance type for a given `model_id`

```python
from sagemaker import instance_types
instance_type = instance_types.retrieve_default(
    model_id=model_id,
    model_version=model_version,
    scope="inference")
print(instance_type)
```

Deploying the JumpStart Model

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
