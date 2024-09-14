#!/usr/bin/env python

# Usage:
#   streamlit run streamlit_qwen2vl.py --server.port 8081 --server.runOnSave true
#
# Setup:
#   pip install git+https://github.com/huggingface/transformers 
#   pip install streamlit ollama qwen-vl-utils torchvision 'accelerate>=0.26.0'
#   pip install flash-attn --no-build-isolation

import argparse
import glob
import os
import streamlit as st
import torch

from PIL import Image
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from typing import Dict, Generator



st.set_page_config(layout="wide")

model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2-VL-7B-Instruct",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
)

processor = AutoProcessor.from_pretrained(
    "Qwen/Qwen2-VL-7B-Instruct",
    min_pixels=256*28*28,
    max_pixels=1280*28*28
)



def invoke_qwen2vl(prompt, image_url):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image_url,
                },
                {
                    "type": "text",
                    "text": prompt
                },
            ],
        }
    ]
    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to("cuda")
    generated_ids = model.generate(
        **inputs,
        max_new_tokens=128
    )
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    response = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )
    return '\n'.join(response)



def clear():
    st.session_state.messages1 = []



def tab_multimodal():
    col1, col2 = st.columns(2)

    with col2:
        # img_data = st.file_uploader('Upload a PNG image', type=['png','jpg'])
        # if img_data is not None:
        #    with Image.open(img_data) as image:
        #        image.save("image.png")

        image_file = 'images/image.jpg'
        if os.path.isfile(image_file):
            st.image(image_file)
        
        st.session_state.use_image = st.toggle("Use Image", value=True, key="Image")

    with col1:
        for message in st.session_state.messages1:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("How could I help you?", key="Multimodal Chat"):
            if st.session_state.use_image:
                with open(image_file, 'rb') as f:
                    st.session_state.messages1.append({
                        "role": "user",
                        "content": prompt,
                        "images": [f.read()]
                    })
            else:
                st.session_state.messages1.append({
                    "role": "user",
                    "content": prompt
                })
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                if st.session_state.selected_model == "":
                    model_id = "Qwen2-VL-8B"
                else:
                    model_id = st.session_state.selected_model
                response = st.write(
                    invoke_qwen2vl(
                        prompt = prompt,
                        image_url = st.session_state.image_url
                    )
                )
            st.session_state.messages1.append(
                {"role": "assistant", "content": response})



def main(args):
    st.title("Qwen2-VL Multimodal")

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = ""
    if "messages1" not in st.session_state:
        st.session_state.messages1 = []
    if "use_image" not in st.session_state:
        st.session_state.use_image = False
    if "image_url" not in st.session_state:
        st.session_state.image_url = args.image_url

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.selected_model = st.selectbox(
            "Please select the model:", [ "Qwen2-VL-8B" ])
    with col2:
        st.markdown("")
        st.markdown("")
        st.button("Clear Chat", on_click=clear, key="Clear Chat")

    tab_multimodal()
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, default='', help="Query the vector database")
    parser.add_argument('--image_url', type=str, default=os.getenv('IMAGE_URL', ''), help="Image URL")
    args = parser.parse_args()

    print(f'image_url = {args.image_url}')
    main(args)
