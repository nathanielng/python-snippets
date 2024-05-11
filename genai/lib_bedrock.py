#!/usr/bin/env python

# Code has mostly been adapted from either the Bedrock Console UI or from:
# https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/bedrock-runtime/bedrock_runtime_wrapper.py

import argparse
import base64
import boto3
import io
import json
import logging
import os

from botocore.config import Config
from botocore.exceptions import ClientError

from typing import List


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


config = Config(read_timeout=1000)
REGION = 'us-west-2'
print(f'Boto3 version: {boto3.__version__}')
print(f'Region: {REGION}')


bedrock = boto3.client(
    service_name='bedrock',
    region_name=REGION
)

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=REGION,
    config=config
)



# ----- Common -----
def list_models():
    response = bedrock.list_foundation_models()
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception('Failed to list models')
    models = response['modelSummaries']
    for model in models:
        model_id = model['modelId']
        model_name = model['modelName']
        print(f'{model_id}: {model_name}')
    return model

def get_model_ids():
    response = bedrock.list_foundation_models()
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception('Failed to list models')
    return [ model['modelId'] for model in response['modelSummaries'] ]

def get_model_names():
    response = bedrock.list_foundation_models()
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception('Failed to list models')
    return [ model['modelName'] for model in response['modelSummaries'] ]

def get_foundational_model(model_id):
    return bedrock.get_foundation_model(modelIdentifier=model_id)



# ----- AI 21 -----
def invoke_jurrasic2_mid(prompt, **kwargs):
    body = {
        "prompt": prompt,
        "maxTokens": 200,
        "temperature": 0,
        "topP": 1.0,
        # "stop_sequences": [],
        "countPenalty": {
            "scale": 0
        },
        "presencePenalty": {
            "scale": 0
        },
        "frequencyPenalty": {
            "scale": 0
        }
    }

    for parameter in ['maxTokens', 'temperature', 'topP', 'countPenalty', 'presencePenalty', 'frequencyPenalty']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    try:
        response = bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId='ai21.j2-mid-v1',
            accept='*/*',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        completions = response_body.get('completions')[0]
        # finishReason = completions.get('finishReason')
        return completions.get('data').get('text')
    except Exception as e:
        print(e)
        return e


def invoke_jurrasic2_ultra(prompt, **kwargs):
    body = {
        "prompt": prompt,
        "maxTokens": 200,
        "temperature": 0,
        "topP": 1.0,
        # "stop_sequences": [],
        "countPenalty": {
            "scale": 0
        },
        "presencePenalty": {
            "scale": 0
        },
        "frequencyPenalty": {
            "scale": 0
        }
    }
    for parameter in ['maxTokens', 'temperature', 'topP', 'countPenalty', 'presencePenalty', 'frequencyPenalty']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    try:
        response = bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId='ai21.j2-ultra-v1',
            accept='*/*',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        completions = response_body.get('completions')[0]
        # finishReason = completions.get('finishReason')
        return completions.get('data').get('text')
    except Exception as e:
        print(e)
        return e


# ----- Amazon Titan -----
def invoke_titan_text_express(prompt, **kwargs):
    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 8192,
            "stopSequences": [],
            "temperature":0,
            "topP": 1
         }
    }
    for parameter in ['maxTokenCount', 'stopSequences', 'temperature', 'topP']:
        if parameter in kwargs:
            body['textGenerationConfig'][parameter] = kwargs[parameter]

    try:
        response = bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId='amazon.titan-text-express-v1',
            accept='*/*',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        return response_body.get('results')[0].get('outputText')
    except Exception as e:
        print(e)
        return e


def invoke_titan_text_embeddings(prompt, **kwargs):
    body = {
        "inputText": prompt
    }

    try:
        response = bedrock_runtime.invoke_model(
            body=json.dumps(body),
            modelId='amazon.titan-embed-text-v1',
            accept='*/*',
            contentType='application/json'
        )
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get('embedding')
        token_count = response_body.get('inputTextTokenCount')
        return embedding, token_count
    except Exception as e:
        print(e)
        return e



# ----- Anthropic Claude v1 & v2 -----
def invoke_claude_v1_n_2(prompt, model_id, **kwargs):
    body = {
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 512,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"],
        "anthropic_version": "bedrock-2023-05-31"
    }
    for parameter in ['max_tokens_to_sample', 'temperature', 'top_k', 'top_p']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    try:
        response = bedrock_runtime.invoke_model(
            modelId = model_id,
            contentType = "application/json",
            accept = "application/json",
            body = json.dumps(body)
        )
        response_body = json.loads(response.get('body').read())
        return response_body['completion']
    except ClientError:
        logger.error(f"Couldn't invoke {model_id}")
        raise

def invoke_claude_instant(prompt, **kwargs):
    return invoke_claude_v1_n_2(prompt, "anthropic.claude-instant-v1", **kwargs)

def invoke_claude_v1(prompt, **kwargs):
    return invoke_claude_v1_n_2(prompt, "anthropic.claude-v1", **kwargs)

def invoke_claude_v2(prompt, **kwargs):
    return invoke_claude_v1_n_2(prompt, "anthropic.claude-v2", **kwargs)



# ----- Anthropic Claude v3 -----
def invoke_claude_v3(prompt, **kwargs):
    messages = {
      "role": "user",
      "content": [
          {
            "type": "text",
            "text": prompt
          }
      ]
    }
    body = {
        "messages": [messages],
        "max_tokens": 512,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": [
            "\\n\\nHuman:"
        ],
        "anthropic_version": "bedrock-2023-05-31"
    }

    for parameter in ['max_tokens', 'temperature', 'top_k', 'top_p']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    response = bedrock_runtime.invoke_model(
        modelId = model_id,
        contentType = "application/json",
        accept = "application/json",
        body = json.dumps(body) #.encode('utf-8')
    )
    response_body = json.loads(response.get('body').read()) #.read().decode('utf-8'))
    # input_tokens = response_body['usage']['input_tokens']
    # output_tokens = response_body['usage']['output_tokens']
    content = response_body.get("content", [])
    completion = [ c['text'] for c in content if c['type'] == 'text' ]
    if len(completion) > 0:
        return '\n'.join(completion)
    else:
        return response_body

def invoke_claude_v3_haiku(prompt, **kwargs):
    return invoke_claude_v3(prompt, "anthropic.claude-3-haiku-20240307-v1:0", **kwargs)

def invoke_claude_v3_sonnet(prompt, **kwargs):
    return invoke_claude_v3(prompt, "anthropic.claude-3-sonnet-20240229-v1:0", **kwargs)



def invoke_claude_v3_sonnet_with_response_stream(prompt, **kwargs):
    messages = {
      "role": "user",
      "content": [
          {
            "type": "text",
            "text": prompt
          }
      ]
    }
    body = {
        "messages": [messages],
        "max_tokens": 500,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": [
            "\\n\\nHuman:"
        ],
        "anthropic_version": "bedrock-2023-05-31"
    }

    for parameter in ['max_tokens', 'temperature', 'top_k', 'top_p']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    response_stream = bedrock_runtime.invoke_model_with_response_stream(
        modelId = "anthropic.claude-3-sonnet-20240229-v1:0",
        contentType = "application/json",
        accept = "application/json",
        body = json.dumps(body) #.encode('utf-8')
    )
    stream = response_stream.get('body')

    output = []
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                chunk_obj = json.loads(chunk.get('bytes').decode())
                text = chunk_obj['completion']
                output.append(text)

    return stream



def invoke_claude_v3_multimodal(prompt, base64_image_data, model_id="anthropic.claude-3-sonnet-20240229-v1:0", **kwargs):
    messages = {
      "role": "user",
      "content": [
          {
            "type": "text",
            "text": prompt
          },
          {
              "type": "image",
              "source": {
                  "type": "base64",
                  "media_type": "image/png",
                  "data": base64_image_data
              }
          }
      ]
    }
    body = {
        "messages": [messages],
        "max_tokens": 500,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": [
            "\\n\\nHuman:"
        ],
        "anthropic_version": "bedrock-2023-05-31"
    }

    for parameter in ['max_tokens', 'temperature', 'top_k', 'top_p']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    response = bedrock_runtime.invoke_model(
        modelId = model_id,
        contentType = "application/json",
        accept = "application/json",
        body = json.dumps(body)
    )
    response_body = json.loads(response.get('body').read()) #.read().decode('utf-8'))
    # input_tokens = response_body['usage']['input_tokens']
    # output_tokens = response_body['usage']['output_tokens']
    content = response_body.get("content", [])
    for c in content:
        if c['type'] == 'text':
            return c['text']
    return response_body



# ----- Cohere -----
def invoke_cohere_command(prompt, **kwargs):
    body = {
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.8
        # "return_likelihood": "GENERATION"   
    }
    for parameter in ['max_tokens', 'temperature']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    response = bedrock_runtime.invoke_model(
        modelId = "cohere.command-text-v14",
        contentType = "application/json",
        accept = "*/*",
        body = json.dumps(body)
    )
    response_body = json.loads(response.get('body').read())
    return response_body['generations'][0]['text']


def invoke_cohere_command_light(prompt, **kwargs):
    body = {
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.8
        # "return_likelihood": "GENERATION"   
    }
    for parameter in ['max_tokens', 'temperature']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    response = bedrock_runtime.invoke_model(
        modelId = "cohere.command-light-text-v14",
        contentType = "application/json",
        accept = "*/*",
        body = json.dumps(body)
    )
    response_body = json.loads(response.get('body').read())
    return response_body['generations'][0]['text']


def invoke_cohere_embed_english(prompts: List[str]):
    body = {
        "texts": prompts,
        "input_type": 'search_document',
        "truncate": 'NONE'
    }

    response = bedrock_runtime.invoke_model(
        modelId = "cohere.embed-english-v3",
        contentType = "application/json",
        accept = "application/json",
        body = json.dumps(body)
    )
    response_body = json.loads(response.get('body').read())
    return response_body['embeddings']


def invoke_cohere_embed_multilingual(prompts: List[str]):
    body = {
        "texts": prompts,
        "input_type": 'search_document',
        "truncate": 'NONE'
    }

    response = bedrock_runtime.invoke_model(
        modelId = "cohere.embed-multilingual-v3",
        contentType = "application/json",
        accept = "*/*",
        body = json.dumps(body)
    )
    response_body = json.loads(response.get('body').read())
    return response_body['embeddings']



# ----- Llama-2 -----
def invoke_llama2_chat(prompt, model_id, **kwargs):
    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "top_p": 0.9,
        "temperature": 0.2
    }
    for parameter in ['max_gen_len', 'top_p', 'temperature']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    response = bedrock_runtime.invoke_model(
        modelId = model_id,
        contentType = "application/json",
        accept = "application/json",
        body = json.dumps(body)
    )
    response_body = json.loads(response.get('body').read())
    return response_body['generation']

def invoke_llama2_13b_chat(prompt, **kwargs):
    return invoke_llama2_chat(prompt, "meta.llama2-13b-chat-v1", **kwargs)

def invoke_llama2_70b_chat(prompt, **kwargs):
    return invoke_llama2_chat(prompt, "meta.llama2-70b-chat-v1", **kwargs)



# ----- Llama-3 -----
def invoke_llama3_instruct(prompt, model_id, **kwargs):
    """
    Invoke Llama3 8B Instruct
    https://llama.meta.com/docs/model-cards-and-prompt-formats/meta-llama-3/#special-tokens-used-with-meta-llama-3
    """
    prompt_template = f"""
    <|begin_of_text|>
    <|start_header_id|>user<|end_header_id|>
    {prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    body = {
        "prompt": prompt_template.format(prompt=prompt),
        "max_gen_len": 512,
        "top_p": 0.9,
        "temperature": 0.5
    }
    for parameter in ['max_gen_len', 'top_p', 'temperature']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    response = bedrock_runtime.invoke_model(
        modelId = model_id,
        contentType = "application/json",
        accept = "*/*",
        body = json.dumps(body)
    )
    response_body = json.loads(response.get('body').read())
    return response_body['generation']

def invoke_llama3_8b_instruct(prompt, **kwargs):
    return invoke_llama3_instruct(prompt, "meta.llama3-8b-instruct-v1:0", **kwargs)

def invoke_llama3_70b_instruct(prompt, **kwargs):
    return invoke_llama3_instruct(prompt, "meta.llama3-70b-instruct-v1:0", **kwargs)



# ----- Mistral -----
def invoke_mistral(prompt, model_id, **kwargs):
    """
    Invokes the Mistral 7B model
    :param prompt: The prompt that you want Mistral to complete.
    :return: List of inference responses from the model.
    """

    prompt_template = "<s>[INST] {prompt} [/INST]"
    body = {
        "prompt": prompt_template.format(prompt=prompt),
        "max_tokens": 512,
        # "top_p": 0.9,
        # "top_k": 50,
        "temperature": 0.1,
    }
    for parameter in ['max_tokens', 'top_p', 'top_k', 'temperature']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    try:
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            contentType = "application/json",
            accept = "application/json",
            body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        outputs = response_body.get("outputs")
        return [output["text"] for output in outputs]

    except ClientError:
        logger.error(f"Couldn't invoke {model_id}")
        raise

def invoke_mistral_7b(prompt, **kwargs):
    return invoke_mistral(prompt, "mistral.mistral-7b-instruct-v0:2", **kwargs)

def invoke_mistral_8x7b(prompt, **kwargs):
    return invoke_mistral(prompt, "mistral.mixtral-8x7b-instruct-v0:1", **kwargs)

def invoke_mistral_large(prompt, **kwargs):
    return invoke_mistral(prompt, "mistral.mistral-large-2402-v1:0", **kwargs)



# ----- Stability AI -----
def invoke_stable_diffusion_xl(prompt, **kwargs):
    text_prompts = [{"text": prompt, "weight": 1.0}]
    if 'negative_prompts' in kwargs:
        negative_prompts = kwargs['negative_prompts'].split(',')
        text_prompts = text_prompts + [{"text": negprompt, "weight": -1.0} for negprompt in negative_prompts]

    body = {
        "text_prompts": text_prompts,
        "cfg_scale": 10,
        "seed": 0,
        "steps": 50
    }

    for parameter in ['cfg_scale', 'seed', 'steps', 'style_preset']:
        if parameter in kwargs:
            body[parameter] = kwargs[parameter]

    try:
        response = bedrock_runtime.invoke_model(
            modelId = "stability.stable-diffusion-xl-v0",
            contentType = "application/json",
            accept = "application/json",
            body = json.dumps(body)
        )
        response_body = json.loads(response.get('body').read())
        artifacts = response_body.get('artifacts')
        base_64_img_str = artifacts[0].get('base64')
        return base_64_img_str
    except ClientError:
        logger.error("Couldn't invoke Stable Diffusion XL")
        raise
    

# ----- Save Image -----
def save_image(base_64_img_str, img_file):
    # from PIL import Image
    # img = Image.open(io.BytesIO(base64.decodebytes(bytes(base_64_img_str, "utf-8"))))  
    # img.save(img_file)
    with open(img_file, "wb") as file:
        file.write(base_64_img_str)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', default='What is science?')
    parser.add_argument('--model', default='claude-instant')
    parser.add_argument('--get-model-ids', action='store_true')
    parser.add_argument('--get-fm', default='')
    args = parser.parse_args()

    if args.get_model_ids:
        print('\n'.join(get_model_ids()))
        exit(0)

    if args.get_fm:
        print(get_foundational_model(args.get_fm))
        exit(0)

    prompt = args.prompt
    if prompt:
        if args.model == 'titan-express':
            print(invoke_titan_text_express(prompt))
        elif args.model == 'titan-embeddings':
            print(invoke_titan_text_embeddings(prompt))

        elif args.model == 'claude-instant':
            print(invoke_claude_instant(prompt))
        elif args.model == 'claudev1':
            print(invoke_claude_v1(prompt))
        elif args.model == 'claudev2':
            print(invoke_claude_v2(prompt))
        elif args.model == 'claudev3_haiku':
            print(invoke_claude_v3_haiku(prompt))
        elif args.model == 'claudev3_sonnet':
            print(invoke_claude_v3_sonnet(prompt))

        elif args.model == 'cohere_command':
            print(invoke_cohere_command(prompt))
        elif args.model == 'cohere_command_light':
            print(invoke_cohere_command_light(prompt))
        elif args.model == 'cohere_embed_english':
            print(invoke_cohere_embed_english( [ prompt ] ))
        elif args.model == 'cohere_embed_multilingual':
            print(invoke_cohere_embed_multilingual( [ prompt ] ))

        elif args.model == 'jurassic-mid':
            print(invoke_jurrasic2_mid(prompt))
        elif args.model == 'jurassic-ultra':
            print(invoke_jurrasic2_ultra(prompt))

        elif args.model == 'llama2_13b_chat':
            print(invoke_llama2_13b_chat(prompt))
        elif args.model == 'llama2_70b_chat':
            print(invoke_llama2_70b_chat(prompt))
        elif args.model == 'llama3_8b_instruct':
            print(invoke_llama3_8b_instruct(prompt))
        elif args.model == 'llama3_70b_instruct':
            print(invoke_llama3_70b_instruct(prompt))

        elif args.model == 'mistral_7b':
            print(invoke_mistral_7b(prompt))
        elif args.model == 'mistral_8x7b':
            print(invoke_mistral_8x7b(prompt))
        elif args.model == 'mistral_large':
            print(invoke_mistral_large(prompt))

        elif args.model == 'stable-diffusion-xl':
            print(invoke_stable_diffusion_xl(prompt))
