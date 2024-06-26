# Machine Learning Inference

## 1. EC2 Deployment

### 1.1 EC2 with HuggingFace

```python
#!/usr/bin/env python

import argparse
import re
from transformers import AutoModelForCausalLM, AutoTokenizer

HF_MODEL_ID = "aisingapore/sea-lion-7b-instruct"
PROMPT_TEMPLATE = "### USER:\n{prompt}\n\n### RESPONSE:\n"
tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(HF_MODEL_ID, trust_remote_code=True)

def invoke_hf_model(prompt, **kwargs):
    payload = {
        "do_sample": False,  # set to true if temperature is not 0
        "temperature": None,
        "max_new_tokens": 2048,
        "top_k": 50,
        "top_p": 0.7,
        "repetition_penalty": 1.2,
    }
    for k in kwargs:
        if k in [ "do_sample", "temperature", "max_new_tokens", "top_k", "top_p", "repetition_penalty" ]:
            payload[k] = kwargs[k]

    payload["eos_token_id"] = tokenizer.eos_token_id
    if payload["do_sample"] == False:
        payload.pop("temperature")
        payload.pop("top_k")
        payload.pop("top_p")

    final_prompt = PROMPT_TEMPLATE.format(prompt=prompt)
    tokens = tokenizer(
        final_prompt,
        return_tensors="pt"
    )
    response = model.generate(
        tokens["input_ids"],
        **payload
    )
    completion = tokenizer.decode(response[0], skip_special_tokens=True)
    return completion[len(final_prompt):]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', type=str)
    args = parser.parse_args()
    completion = invoke_hf_model(args.prompt)
    print(completion)
```

### 1.2 EC2 with Ollama

```python
cat > ollama_llama3.py << EOF
#!/usr/bin/env python

import argparse
from langchain.llms import Ollama
ollama = Ollama(base_url='http://localhost:11434',
model="llama3:70b")

prompts = [
    "Tell me about machine learning",
    "Tell me about generative AI"
]

def invoke_ollama(prompt):
    return ollama(prompt)

def test_all(csv_file, **kwargs):
    data = []
    for prompt in prompts:
        completion = invoke_ollama(prompt)
        print(f"----- Prompt -----\n{prompt}\n----- Completion -----\n{completion}\n\n\n")
        data.append(
            [prompt, completion]
        )
    import csv
    with open(csv_file, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for x in data:
            writer.writerow(x)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default='ollama_llama3_70b.csv')
    parser.add_argument('--test_all', action='store_true')
    args = parser.parse_args()
    if args.test_all:
        test_all(args.file)
    else:
        completion = invoke_ollama(args.prompt)
        print(completion)
EOF
python ollama_llama3.py --test_all
```


Source of code: https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct

```python
import transformers
import torch

model_id = "meta-llama/Meta-Llama-3-70B-Instruct"

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device="auto",
)

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

prompt = pipeline.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

outputs = pipeline(
    prompt,
    max_new_tokens=256,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.6,
    top_p=0.9,
)
print(outputs[0]["generated_text"][len(prompt):])
```

## 2. SageMaker-HuggingFace Deployment

Dependencies

```bash
pip install --upgrade pip
pip install --upgrade sagemaker
```

Example Python code

```python
#!/usr/bin/env python

import argparse
import json
import sagemaker
import boto3

from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from sagemaker.huggingface.model import HuggingFaceModel

AWS_REGION = "us-west-2"
PROMPT_TEMPLATE = "### USER:\n{prompt}\n\n### RESPONSE:\n"

try:
    role = sagemaker.get_execution_role()
except ValueError:
    iam = boto3.client('iam')
    role = iam.get_role(RoleName='AmazonSageMaker-ExecutionRole-...')['Role']['Arn']

hub = {
  'HF_MODEL_ID':'aisingapore/sealion7b-instruct-nc',
  'SM_NUM_GPUS': json.dumps(4),
  'HF_MODEL_TRUST_REMOTE_CODE': json.dumps(True),
  # 'HF_MODEL_QUANTIZE': 'bitsandbytes',
  # 'MESSAGES_API_ENABLED': True
}

huggingface_model = HuggingFaceModel(
   image_uri=get_huggingface_llm_image_uri("huggingface",version="1.4.0"),
   env=hub,
   role=role
)

predictor = huggingface_model.deploy(
   initial_instance_count=1,
   instance_type="ml.g5.12xlarge",
   container_startup_health_check_timeout=360,
   model_download_timeout=1800
)

def invoke_hf_model(prompt, **kwargs):
    final_prompt = PROMPT_TEMPLATE.format(prompt=prompt)
    completion = predictor.predict({
    	"inputs": final_prompt
    })
    return completion

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', type=str)
    args = parser.parse_args()
    completion = invoke_hf_model(args.prompt)
    print(completion)

    predictor.delete_model()
    predictor.delete_endpoint()
```

## 3. SageMaker-JumpStart Deployment

Example Python code

```python
#!/usr/bin/env python

import argparse
from sagemaker.jumpstart.model import JumpStartModel

PROMPT_TEMPLATE = "### USER:\n{prompt}\n\n### RESPONSE:\n"
model_id = "huggingface-llm-sealion-7b-instruct"
model = JumpStartModel(model_id=model_id)
predictor = model.deploy(accept_eula=True)

def invoke_jumpstart_model(prompt):
    response = predictor.predict(PROMPT_TEMPLATE.format(prompt=prompt))
    response = response[0] if isinstance(response, list) else response
    return response["generated_text"].strip()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', type=str)
    args = parser.parse_args()
    completion = invoke_jumpstart_model(args.prompt)
    print(completion)
    predictor.delete_predictor()
```

```python
example_payloads = model.retrieve_all_examples()
for payload in example_payloads:
    response = predictor.predict(payload.body)
    response = response[0] if isinstance(response, list) else response
    print("Input:\n", payload.body, end="\n\n")
    print("Output:\n", response["generated_text"].strip(), end="\n\n\n")
```
