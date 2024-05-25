#!/usr/bin/env python

# Example:
# curl -LO https://huggingface.co/xtuner/llava-phi-3-mini-gguf/resolve/main/llava-phi-3-mini-int4.gguf
# curl -LO https://huggingface.co/xtuner/llava-phi-3-mini-gguf/resolve/main/OLLAMA_MODELFILE_INT4
# sed 's/FROM .\/llava-phi-3-mini-mmproj-f16.gguf//g' ./OLLAMA_MODELFILE_INT4 > OLLAMA_MODELFILE_INT4_v2
# ollama create llava-phi3-int4 -f ./OLLAMA_MODELFILE_INT4_v2

# pip install ollama
# python hello_ollama.py --prompt "What is ollama?" --model-id llava-phi3-int4

import argparse
import json
import ollama



def ollama_ls():
    response = ollama.list()
    print(json.dumps(response, indent=2))
    return response



def ollama_show(model_id):
    response = ollama.show(model_id)
    print(json.dumps(response, indent=2))
    return response


def invoke_ollama(prompt, model_id):
    messages = [
        {
            'role': 'user',
            'content': prompt
        }
    ]
    try:
        response = ollama.chat(model=model_id, messages = messages)
        return response['message']['content']
    except Exception as e:
        print(e)
        raise



def streaming_function(stream):
    for chunk in stream:
        yield chunk['message']['content']



def invoke_ollama_with_streaming(prompt, model_id):
    messages = [
        {
            'role': 'user',
            'content': prompt
        }
    ]
    try:
        return ollama.chat(model=model_id, messages = messages, stream=True)
    except Exception as e:
        print(e)
        raise



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ls', action='store_true')
    parser.add_argument('--model-id', default='', type=str)
    parser.add_argument('--prompt', type=str)
    parser.add_argument('--show', action='store_true')
    args = parser.parse_args()

    if args.ls:
        ollama_ls()
    elif args.show:
        if args.model_id:
            ollama_show(args.model_id)
        else:
            print(f'Invalid model_id="{args.model_id}"')
    elif args.prompt:
        stream = invoke_ollama_with_streaming(args.prompt, args.model_id)
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)
        print()
