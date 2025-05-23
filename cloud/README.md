# Cloud

## 1. Downloading Files

```python
import requests
import os

def download_file(url, destination):
    """
    Download a file from a URL to a local destination
    """
    try:
        # Send GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Get the file size if available
        file_size = int(response.headers.get('content-length', 0))

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)

        # Write the content to the file
        with open(destination, 'wb') as file:
            if file_size == 0:
                file.write(response.content)
                print(f"Downloaded {destination}")
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        # Print progress
                        progress = int(50 * downloaded / file_size)
                        print(f"\rDownloading: [{'#' * progress}{'.' * (50 - progress)}] {downloaded}/{file_size} bytes", end='')
                print(f"\nDownloaded {destination}")

        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False
```

## 2. Lambda Functions

### 2.1 Invoke Lambda function

```python
import boto3
import json

client = boto3.client('lambda', region_name='us-east-1')

def invoke_lambda(payload):
    response = client.invoke(
        FunctionName='my-lambda-function',
        InvocationType='RequestResponse',
        Payload=payload
    )
    return response

if __name__ == '__main__':
    payload = {
        'key': 'value'
    }
    response = invoke_lambda(json.dumps(payload))
    print(json.dumps(response, indent=2, default=str))
```


## 3. CloudFront

### 3.1 Invalidations

```python
import boto3, json
cloudfront = boto3.client('cloudfront')
response = cloudfront.create_invalidation(
    DistributionId='E............D',
    InvalidationBatch={
        'Paths': {
            'Quantity': 1,
            'Items': [ '/path/to/folder/*' ]
        },
    }
)
print(json.dumps(response, indent=2, default=str))
```


## 4. Webscraping README

### 4.1 Selenium Webdriver

#### 4.1.1 Links

- **Github**: https://github.com/SeleniumHQ/selenium
- **Documentation**: https://www.selenium.dev/selenium/docs/api/py/ (Python)

#### 4.1.2 Setup

1. **Safari** (Mac OS X): the web driver should already be located at `/usr/bin/safaridriver`, and may be enabled with the command `/usr/bin/safaridriver --enable`. In Safari, in the 'Develop' menu, enable 'Allow Remote Automation'.  The supported commands are listed [here](https://developer.apple.com/documentation/webkit/macos_webdriver_commands_for_safari_12_and_later)
2. **Chrome**: the chrome driver may be downloaded from [https://chromedriver.chromium.org](https://chromedriver.chromium.org)

```bash
pip install selenium
```


### 4.2 Mechanize

#### 4.2.1 Links

- **Github**: https://github.com/python-mechanize/mechanize
- **Documentation**: https://mechanize.readthedocs.io/en/latest/

#### 4.2.2 Setup

```bash
pip install mechanize
```
