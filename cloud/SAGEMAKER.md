# Amazon SageMaker

## SageMaker JumpStart

Deploy a JumpStart model

```python
from sagemaker.jumpstart.model import JumpStartModel

model_id = "huggingface-text2text-flan-t5-xl"
my_model = JumpStartModel(model_id=model_id)
predictor = my_model.deploy()
```

Getting the default instance type for a given `model_id`

```
from sagemaker import instance_types
instance_type = instance_types.retrieve_default(
    model_id=model_id,
    model_version=model_version,
    scope="inference")
print(instance_type)
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
