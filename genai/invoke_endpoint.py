#!/bin/bash

# Some parts of this code (such as the streaming) are taken from the following MIT-O licensed code:
# https://github.com/aws-samples/sagemaker-genai-hosting-examples/blob/main/Gemma3/Gemma-3-27B-Instruct.ipynb

import boto3
import json
import os
import time
from sagemaker.serializers import JSONSerializer, IdentitySerializer
from sagemaker.deserializers import JSONDeserializer
from sagemaker.predictor import Predictor

region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')

# Option 1: Automatically retrieve the first endpoint (if this is your only endpoint)
sagemaker_client = boto3.client('sagemaker', region_name=region)
sagemaker_runtime_client = boto3.client('sagemaker-runtime', region_name=region)
response = sagemaker_client.list_endpoints()
endpoint_names = [ endpoint['EndpointName'] for endpoint in response['Endpoints'] ]
if len(endpoint_names):
    endpoint_name = endpoint_names[0]
    print(f'Using endpoint: {endpoint_name}')

# Option 2: Set the endpoint name manually (Uncomment below to use Option 2)
# endpoint_name = "gemma-3-27b-it-... (replace with your enpoint name)"

predictor = Predictor(
    endpoint_name=endpoint_name,
    serializer=JSONSerializer(),
    deserializer=JSONDeserializer()
)

def invoke_model(prompt: str, print_response=True, **kwargs):
    payload = {
        "messages" : [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1,
        "top_p": 0.9,
    }
    for k in kwargs:
        if k in ['max_tokens', 'temperature', 'top_p']:
            payload[k] = kwargs[k]
    response = predictor.predict(payload)
    
    if print_response:
        # Print usage statistics
        usage = response['usage']
        print(response['choices'][0]['message']['content'].strip())
        print(f"=== Token Usage: {usage['prompt_tokens']} (prompt), {usage['completion_tokens']} (completions), {usage['total_tokens']} (total) ===")
    return response['choices'][0]['message']['content']

def invoke_model_with_streaming(endpoint_name, prompt, system_prompt = "You are a helpful assistant.", **kwargs):
    body = {
        "messages": [
            {
                "role": "system",
                "content": [{"type": "text", "text": system_prompt}]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ],
        "max_tokens": 1500,
        "temperature": 0.6,
        "top_p": 0.9,
        "stream": True
    }
    for k in kwargs:
        if k in ['max_tokens', 'temperature', 'top_p']:
            body[k] = kwargs[k]

    # Invoke the model
    response_stream = sagemaker_runtime_client.invoke_endpoint_with_response_stream(
        EndpointName = endpoint_name,
        ContentType = "application/json",
        Body = json.dumps(body)
    )

    first_token_received = False
    ttft = None
    token_count = 0
    start_time = time.time()

    print("Response:", end=' ', flush=True)
    full_response = ""

    for event in response_stream['Body']:
        if 'PayloadPart' in event:
            chunk = event['PayloadPart']['Bytes'].decode()
            
            try:
                # Handle SSE format (data: prefix)
                if chunk.startswith('data: '):
                    data = json.loads(chunk[6:])  # Skip "data: " prefix
                else:
                    data = json.loads(chunk)
                
                # Extract token based on OpenAI format
                if 'choices' in data and len(data['choices']) > 0:
                    if 'delta' in data['choices'][0] and 'content' in data['choices'][0]['delta']:
                        token_count += 1
                        token_text = data['choices'][0]['delta']['content']
                                        # Record time to first token
                        if not first_token_received:
                            ttft = time.time() - start_time
                            first_token_received = True
                        full_response += token_text
                        print(token_text, end='', flush=True)
            
            except json.JSONDecodeError:
                continue
                
    # Print metrics after completion
    end_time = time.time()
    total_latency = end_time - start_time

    print("\n\nMetrics:")
    print(f"Time to First Token (TTFT): {ttft:.2f} seconds" if ttft else "TTFT: N/A")
    print(f"Total Tokens Generated: {token_count}")
    print(f"Total Latency: {total_latency:.2f} seconds")
    if token_count > 0 and total_latency > 0:
        print(f"Tokens per second: {token_count/total_latency:.2f}")


def invoke_model_with_strands_tools(endpoint_name, prompt, system_prompt = "You are a helpful assistant.", region="us-west-2", **kwargs):
    """
    This code has been adapted from:
      https://docs.vllm.ai/en/stable/features/tool_calling.html
    Dependencies
      uv pip install -U strands-agents
      uv pip install 'boto3-stubs[sagemaker-runtime]'
    """
    from strands import Agent
    from strands.models.sagemaker import SageMakerAIModel
    from strands_tools import calculator

    payload_config={
        "max_tokens": 1000,
        "temperature": 0.7,
        "stream": True,
    }
    for k in kwargs:
        if k in ['max_tokens', 'temperature']:
            payload_config[k] = kwargs[k]

    model = SageMakerAIModel(
        endpoint_config={
            "endpoint_name": endpoint_name,
            "region_name": region,
        },
        payload_config=payload_config
    )
    try:
        agent = Agent(model=model, tools=[calculator], system_prompt=system_prompt)
        return agent(prompt)
    except Exception as e:
        error_message = f"Exception when invoking {endpoint_name}:\n{e}"
        return error_message

def main():
    if action == 'invoke_model':
        _ = invoke_model("Write me a poem about Machine Learning.", max_tokens=500, temperature=0.1, top_p=0.9)
    elif action == 'invoke_model_with_streaming':
        _ = invoke_model_with_streaming(
            endpoint_name = endpoint_name,
            prompt = "Write a poem about Machine Learning.",
            system_prompt = "You are a helpful assistant.",
            max_tokens=1000,
            temperature=0.1,
            top_p=0.9
        )
    elif action == 'invoke_model_with_strands':
        response = invoke_model_with_strands_tools(
            endpoint_name = endpoint_name,
            prompt = "What is 111,111,111 multiplied by 111,111,111?",
            system_prompt = "You are a helpful assistant.",
            max_tokens=1000,
            temperature=0.1,
            top_p=0.9
        )
        print(response)

if __name__ == "__main__":
    main(action='invoke_model_with_strands')
