#!/usr/bin/env python

# Usage:
#   ssh -L 8080:localhost:8080 ubuntu@ip_address
#   eval "$($HOME/miniforge3/bin/conda shell.bash hook)"

#   # First run
#   python3 streamlit_bedrock.py --init  # to populate ChromaDB
#   streamlit run streamlit_bedrock.py --server.port 8080 --server.runOnSave true

# Dependencies
#   pip install chromadb ollama
#   export HNSWLIB_NO_NATIVE=1; pip install chromadb  # for Mac OS
#   ollama pull mxbai-embed-large
#   ollama pull llava



import argparse
import chromadb
import glob
import json
import ollama
import os
import streamlit as st

from chromadb.utils import embedding_functions
from langchain_community.chat_models import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores.utils import filter_complex_metadata
from typing import Dict, Generator
from PIL import Image



# ----- Setup -----
EMBEDDING_MODEL = "mxbai-embed-large"
CHROMADB_PATH = "chromadb_data/"
COLLECTION_NAME = "docs"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
# HF_TOKEN = os.getenv("HF_TOKEN")
RAG_PROMPT_TEMPLATE = 'Given the following context:\n{context}\n\nRespond to the following prompt:\n{prompt}'

# ollama.pull("llava")
# ollama.pull(EMBEDDING_MODEL)



# ----- Langchain -----
# From: https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter/
SEPARATORS = [
    "\n\n\n\n",
    "\n\n\n",
    "\n\n",
    "\n",
    " ",
    ".",
    ",",
    "\u200B",  # Zero-width space
    "\uff0c",  # Fullwidth comma
    "\u3001",  # Ideographic comma
    "\uff0e",  # Fullwidth full stop
    "\u3002",  # Ideographic full stop
    "",
]

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = CHUNK_SIZE,
    chunk_overlap  = CHUNK_OVERLAP,
    length_function = len,
    is_separator_regex=False,
    separators=SEPARATORS
)



# ----- Bedrock -----
import boto3
BEDROCK_REGION = "us-west-2"

from botocore.config import Config
import base64
config = Config(
    read_timeout=1000
)

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=BEDROCK_REGION,
    config=config
)

def invoke_claude_v3_sonnet_with_response_stream(messages, **kwargs):
    body = {
        "messages": messages,
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
    return stream


def bedrock_generator(model_name: str, messages: Dict) -> Generator:
    stream = invoke_claude_v3_sonnet_with_response_stream(messages)
    for event in stream:
        chunk = event.get('chunk')
        if chunk:
            chunk_obj = json.loads(chunk.get('bytes').decode())
            # yield str(chunk_obj) + '-----\n'  # Use this for debugging
            if chunk_obj['type'] == 'content_block_delta':
                yield chunk_obj['delta']['text']


def ollama_generator(model_name: str, messages: Dict) -> Generator:
    stream = ollama.chat(
        model=model_name, messages=messages, stream=True)
    for chunk in stream:
        yield chunk['message']['content']



# ----- Chroma DB -----
client = chromadb.PersistentClient(path=CHROMADB_PATH)

try:
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        # embedding_function=embedding_func,
        # metadata={"hnsw:space": "cosine"}
    )
except Exception as e:
    print(e)
    raise



def init_vectordb(doc_list="txt/*.txt"):
    global collection

    for file in glob.glob(doc_list):
        with open(file, "r") as f:
            doc = f.read()

        # Use Langchain to split into chunks
        documents = text_splitter.create_documents([doc])
        for i, chunk in enumerate(documents):
            chunk_text = chunk.page_content
            print(f'\n----- {i} -----\n{chunk_text}\n')
            response = ollama.embeddings(
                model=EMBEDDING_MODEL,
                prompt=chunk_text
            )
            collection.add(
                ids=[str(i)],
                embeddings=[
                    response["embedding"]
                ],
                documents=[chunk_text]
            )

def query_collection(query, n_results=5):
    embedding = ollama.embeddings(
        prompt=query,
        model=EMBEDDING_MODEL
    )["embedding"]
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )
    ids = results['ids']
    distances = results['distances']
    metadatas = results['metadatas']
    documents = results['documents']
    uris = results['uris']

    summary = []
    for doc in documents[0]:
        summary.append(f'\n\nDOCUMENT:\n{doc}\n\n\n')
    return '\n'.join(summary)


def clear():
    st.session_state.messages1 = []
    st.session_state.messages2 = []
    st.session_state.messages3 = []
    st.session_state.messages3a = []
    st.session_state.context = ''


def tab_chat(generator):
    col1, col2 = st.columns(2)

    with col2:
        if os.path.isfile("txt/context.txt"):
            with open("txt/context.txt", "r") as f:
                file_context = f.read()
        else:
            file_context = ''

        context = st.text_area(label="Context", value=file_context, height=50)
        prompt_template = st.text_area(
            label="Prompt Template",
            value="Answer the question based on the following context: {context}\nThe question is: {question}")
        use_context = st.toggle("Use Context", value=True)

    with col1:
        for message in st.session_state.messages1:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("How could I help you?", key="Text Chat"):
            if use_context:
                final_prompt = prompt_template.format(context=context, question=prompt)
            else:
                final_prompt = prompt
            st.session_state.messages1.append({
                "role": "user",
                "content": final_prompt
            })
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                response = st.write_stream(generator(
                    st.session_state.selected_model, st.session_state.messages1))



def tab_filequery(generator):

    col1, col2 = st.columns(2)

    with col1:
        # context = st.text_area(label="Context", value="", height=50)
        # File uploader
        # file_list = st.file_uploader(
        #     label="Upload your files here",
        #     accept_multiple_files=True
        # )

        # File selector
        files = [ file for file in glob.glob('txt/*.md') ]
        basenames = [ file[4:] for file in files ]
        md_file = st.selectbox(label="Select a file", options=basenames)
        with open(f'txt/{md_file}', 'r') as f:
            context = f.read()

        file_prompt_template = st.text_area(
            label="Prompt Template",
            value="Article: {context}\nBased on the article provided, please answer the following question: {question}")
        use_file_prompt_template = st.toggle("Use Prompt Template", value=True)

        prompt_list = st.text_area(
            label="Provide a list of questions. Each question should be on a new line",
            value="""Express the key takeaways of the article as bullet points\nBriefly describe the sentiment of the author\nHow does the article conclude? Does the author suggest any next steps, or can any action points be inferred?"""
        )
        prompt_list = [ prompt.strip() for prompt in prompt_list.split('\n') ]

    with col2:

        with st.form("information_extraction"):
            submit_queries = st.form_submit_button("Submit")

            if submit_queries:
                for prompt in prompt_list:
                    if use_file_prompt_template:
                        final_prompt = file_prompt_template.format(context=context, question=prompt)
                    else:
                        final_prompt = prompt

                    messages = [{
                        "role": "user",
                        "content": final_prompt
                    }]
                    st.markdown(f'#### {prompt}')
                    response = st.write_stream(generator(
                        st.session_state.selected_model, messages))



def tab_rag(generator):
    n_results = st.number_input("No. of RAG results", value=3, min_value=1, max_value=10)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Enter your question**")
        for message in st.session_state.messages2:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("How could I help you?", key="RAG Chat"):
            context = query_collection(prompt, n_results)
            st.session_state.context = context
            messages2 = [{
                "role": "user",
                "content": RAG_PROMPT_TEMPLATE.format(context=context, prompt=prompt)
            }]
            st.session_state.messages2 = [{
                "role": "user",
                "content": prompt
            }]
            print(f"-----CONTEXT RETRIEVED-----\n{context}\n-----")
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                response = st.write_stream(generator(
                    st.session_state.selected_model, messages2))

    with col2:
        st.markdown("**Context**\n\n" + st.session_state.context)



def tab_multimodal(generator):
    model_id = st.session_state.selected_model
    
    col1, col2 = st.columns(2)

    with col2:
        img_data = st.file_uploader('Upload a PNG image', type=['png'])
        if img_data is not None:
            with Image.open(img_data) as image:
                image.save("image.png")

        if os.path.isfile('image.png'):
            st.image('image.png')
        
        st.session_state.use_image = st.toggle("Use Image", value=True, key="Image")

    with col1:
        st.markdown("**Example prompts**\n- Provide a description of the following picture and give some recommendations\n- Write an interesting story about the picture shown")
        for message in st.session_state.messages3:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("How could I help you?", key="Multimodal Chat"):
            if st.session_state.use_image:
                with open('image.png', 'rb') as f:
                    image_data = f.read()

                # Streamlit needs messages to be in this format
                st.session_state.messages3.append({
                    "role": "user",
                    "content": prompt,
                    "images": [image_data]
                })

                # Claude Sonnet format for Bedrock invocation
                # (see: https://docs.aws.amazon.com/code-library/latest/ug/python_3_bedrock-runtime_code_examples.html and https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/bedrock-runtime/models/anthropic/claude_3.py#L94)
                if st.session_state.selected_model == 'Bedrock/Claude3Sonnet':
                    st.session_state.messages3a.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": base64.b64encode(image_data).decode('utf-8'),
                                },
                            },
                        ]
                    })
            else:
                st.session_state.messages3.append({
                    "role": "user",
                    "content": prompt
                })
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                if model_id == 'Bedrock/Claude3Sonnet':
                    response = st.write_stream(generator(
                        model_id, st.session_state.messages3a))
                else:
                    # Llava and other models
                    response = st.write_stream(generator(
                        model_id, st.session_state.messages3))
            st.session_state.messages3.append(
                {"role": "assistant", "content": response})



def main():
    st.title("Streamlit Bedrock Demo")

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = ""
    if "messages1" not in st.session_state:
        st.session_state.messages1 = []
    if "messages2" not in st.session_state:
        st.session_state.messages2 = []
    if "messages3" not in st.session_state:
        st.session_state.messages3 = []
    if "messages3a" not in st.session_state:
        st.session_state.messages3a = []
    if "context" not in st.session_state:
        st.session_state.context = ''
    if "use_image" not in st.session_state:
        st.session_state.use_image = False

    col1, col2 = st.columns(2)

    with col1:
        ollama_models = [ model["name"] for model in ollama.list()["models"] ]
        all_models = [ "Bedrock/Claude3Sonnet" ] + ollama_models
        st.session_state.selected_model = st.selectbox(
            "Please select the model:", all_models)
    with col2:
        st.markdown("")
        st.markdown("")
        st.button("Clear Chat", on_click=clear, key="Clear Chat")

    if st.session_state.selected_model in ollama_models:
        generator = ollama_generator
    else:
        generator = bedrock_generator

    # tab1, tab2, tab3 = st.tabs(["Chat", "RAG", "Multimodal"])
    tab1, tab2, tab3 = st.tabs(["Chat", "Query a File", "Multimodal"])
    with tab1:
        tab_chat(generator)
    with tab2:
        # tab_rag(generator)
        tab_filequery(generator)
    with tab3:
        tab_multimodal(generator)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--init', action='store_true', help="Initialize the vector database")
    parser.add_argument('--query', type=str, default='', help="Query the vector database")
    args = parser.parse_args()

    if args.init:
        init_vectordb()
    elif args.query:
        result = query_collection(args.query)
        print(result)
    else:
        main()
