#!/usr/bin/env python

# pip install boto3 html2text langchain langchain-community markdown tiktoken unstructured

import argparse
import boto3
import glob
import html2text
import json
import os
import re
import requests
import tiktoken
import time

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_community.embeddings import BedrockEmbeddings, SagemakerEndpointEmbeddings
from langchain_community.vectorstores import FAISS

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
# from langchain.llms.sagemaker_endpoint import ContentHandlerBase

from multiprocessing import cpu_count
from typing import Any, Dict, List, Optional
from tqdm.contrib.concurrent import process_map



BEDROCK_REGION = 'us-west-2'

# ----- Setup Bedrock -----
bedrock = boto3.client(
    service_name='bedrock-runtime', 
    region_name=BEDROCK_REGION
)



# ----- Download html content, given a URL -----
def download_url(url):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
        "Accept-Encoding": "gzip, deflate, br", 
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
        "Dnt": "1", 
        "Host": "httpbin.org", 
        "Upgrade-Insecure-Requests": "1", 
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        pass
    else:
        print(f"Error downloading url '{url}'")
    
    return response.text


def load_url_list(filename='urls.txt'):
    with open(filename, 'r') as f:
        url_list = [ x.strip() for x in f.readlines() ]
        return url_list


def convert_urls_to_txt_filenames(url_list):
    txt_list = []
    for url in url_list:
        txt = re.sub('https://','', url)  # remove https://
        txt = re.sub('/$', '', txt)  # Remove trailing slash
        txt = re.sub('[/.]', '-', txt)
        txt_list.append(f'{txt}.html')
    return txt_list


# ----- Format Converters -----
def convert_html_to_markdown(folder):
    files = glob.glob(f'{folder}/*.html')
    for file in files:
        basename, _ = os.path.splitext(file)
        with open(file, 'r') as f:
            html_text = f.read()
            # markdown_text = markdownify.markdownify(html_text)
            markdown_text = html2text.html2text(html_text)
            markdown_text = re.sub('^Skip to content\n', '', markdown_text)

        with open(f'{basename}.md', 'w') as f:
            f.write(markdown_text)
        
        print(f'Created: {basename}.md')


# ----- Load Folder -----
def load_folder_as_text(folder, extension='md') -> List[str]:
    file_list = glob.glob(f'{folder}/*.{extension}')

    document_list = []
    for file in file_list:
        with open(file, 'r') as f:
            document_list.append(
                f.read()
            )
    return document_list, file_list


def load_folder_as_doc(folder, extension='md'):
    loader = DirectoryLoader(folder, glob=f'*.{extension}', loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap  = 300,
    )
    docs = text_splitter.split_documents(documents)

    # Information
    avg_doc_length = lambda documents: sum([len(doc.page_content) for doc in documents])//len(documents)
    avg_char_count_pre = avg_doc_length(documents)
    avg_char_count_post = avg_doc_length(docs)

    print(f'Average length among {len(documents)} documents loaded is {avg_char_count_pre} characters.')
    print(f'After the split we have {len(docs)} documents more than the original {len(documents)}.')
    print(f'Average length among {len(docs)} documents (after split) is {avg_char_count_post} characters.')

    return docs


# ----- Count Tokens -----
def count_tokens(folder):
    """
    Load Markdown Files
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    document_list, file_list = load_folder_as_text(folder, extension='md')

    for document, file in zip(document_list, file_list):
        encoded_markdown_text = encoding.encode(document)
        n = len(encoded_markdown_text)
        print(f'{file}, {n}')



# ----- Main -----

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', default='md', help='Folder containing documents')
    parser.add_argument('-v', '--vector_store', default='faiss_index', help='Folder for vector store')
    parser.add_argument('-e', '--embeddings', default='titan', help='Embeddings')
    parser.add_argument('--count_tokens', action='store_true')
    parser.add_argument('--html2markdown', action='store_true')
    args = parser.parse_args()

    if args.embeddings == 'openai':
        embeddings = OpenAIEmbeddings()
    elif args.embeddings == 'titan':
        embeddings = BedrockEmbeddings(
            model_id="amazon.titan-embed-text-v1",
            client=bedrock
        )
    elif args.embeddings == 'cohere':
        embeddings = BedrockEmbeddings(
            model_id="cohere.embed-english-v3",
            client=bedrock
        )
    else:
        embeddings = OpenAIEmbeddings()

    if args.vector_store:
        print(f'Loading docs from folder {args.folder}.....')
        docs = load_folder_as_doc(args.folder)

        print(f'\nGenerating embeddings for vector store.....')
        t_start = time.process_time()
        vectorstore = FAISS.from_documents(docs, embeddings)
        print(f'Time elapsed: {time.process_time() - t_start}')

        print(f'\nSaving vector store..... (folder = {args.vector_store})')
        if not os.path.isdir(args.vector_store):
            os.mkdir(args.vector_store)
        vectorstore.save_local(args.vector_store)

    if args.count_tokens:
        count_tokens(args.folder)
    if args.html2markdown:
        convert_html_to_markdown(args.folder)

    # Usage:
    # python lib_faiss.py --f md -e openai -v faiss_index_openai  # Requires OPEN_API_KEY
    # python lib_faiss.py --f md -e titan -v faiss_index_titan
    # python lib_faiss.py --f md -e cohere -v faiss_index_cohere
