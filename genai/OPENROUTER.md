# OpenRouter

## Example

Code:

```python
import argparse
import base64
import os

from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY')
)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_completion(model_id, prompt, base64_image):
    completion = client.chat.completions.create(
        extra_body={},
        model=model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )
    return completion


def main(args):
    completion = get_completion(
        model_id = args.model_id,
        prompt = args.prompt,
        base64_image = encode_image(args.image_path)
    )
    print(completion.choices[0].message.content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_id', type=str, default="qwen/qwen-vl-max")
    parser.add_argument('--prompt', type=str, default="Provide me with the text characters in this image")
    parser.add_argument('--image_path', type=str)
    args = parser.parse_args()
    main(args)
```

Usage:

```
source .venv/bin/activate
uv pip install openai
python openrouter-example.py --image_path IMG_0001.png
```
