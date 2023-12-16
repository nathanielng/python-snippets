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

# Delete all endpoint configurations
for config in endpoint_configs:
    response = sm_client.delete_endpoint_config(EndpointConfigName=config)
```
