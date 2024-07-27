#!/usr/bin/env python

import boto3
import logging

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

bedrock_client = boto3.client(service_name='bedrock-runtime')

SYSTEM_PROMPT = """You are a helpful and honest assistant. If you don't know the answer, say that you don't know."""



def generate_conversation(prompt, model_id, stream=False, **kwargs):
    logger.info(f"Generating message with model {model_id}")

    system_prompts = [{"text": SYSTEM_PROMPT }]
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": prompt
                }
            ]
        }
    ]

    inference_config = {}
    for parameter in ['maxTokens', 'stopSequences', 'temperature', 'topP']:
        if parameter in kwargs:
            inference_config[parameter] = kwargs[parameter]

    additional_model_fields = {}
    for parameter in ['top_k']:
        if parameter in kwargs:
            additional_model_fields[parameter] = kwargs[parameter]

    if stream:
        invoke_fn = bedrock_client.converse_stream
    else:
        invoke_fn = bedrock_client.converse

    try:
        response = invoke_fn(
            modelId=model_id,
            messages=messages,
            system=system_prompts,
            inferenceConfig=inference_config,
            additionalModelRequestFields=additional_model_fields
        )
    except ClientError as err:
        message = err.response['Error']['Message']
        logger.error(f"A client error occurred: {message}")
        print(f"A client error occured: {message}")
    return response



def invoke_model(prompt, model_id):
    model_id = 
    response = generate_conversation(
        prompt = prompt,
        model_id = model_id,
        stream = False,
        temperature = 0.5,
        top_k = 200
    )
    output_messages = response['output']['message']
    role = output_messages['role']
    completion = '\n'.join([ c['text'] for c in output_messages['content'] ])

    usage = response['usage']
    logger.info(f"Latency (ms): {response['metrics']['latencyMs']}")
    logger.info(f"Input tokens: {usage['inputTokens']}")
    logger.info(f"Output tokens: {usage['outputTokens']}")
    logger.info(f"Total tokens: {usage['totalTokens']}")
    logger.info("Stop reason: %s", response['stopReason'])
    return completion



def invoke_model_with_response_stream(prompt, model_id):
    response = generate_conversation(
        prompt = prompt,
        model_id = model_id,
        stream = True,
        temperature = 0.5,
        top_k = 200
    )
    completion = ''

    stream = response.get('stream')
    if stream:
        for event in stream:
            if 'messageStart' in event:
                logger.info(f"[Role: {event['messageStart']['role']}]")

            if 'contentBlockDelta' in event:
                delta = event['contentBlockDelta']['delta']['text']
                completion += delta
                print(delta, end="")

            if 'messageStop' in event:
                print()
                logger.info(f"Stop reason: {event['messageStop']['stopReason']}")

            if 'metadata' in event:
                metadata = event['metadata']
                if 'metrics' in event['metadata']:
                    logger.info(f"Latency (ms): {metadata['metrics']['latencyMs']}")
                if 'usage' in metadata:
                    logger.info(f"Input tokens: {metadata['usage']['inputTokens']}")
                    logger.info(f"Output tokens: {metadata['usage']['outputTokens']}")
                    logger.info(f"Total tokens: {metadata['usage']['totalTokens']}")
    return completion



if __name__ == '__main__':
    prompt = "What is machine learning?"
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    completion = invoke_model_with_response_stream(prompt, model_id)
    # completion = invoke_model(prompt, model_id)
    # print(completion)
