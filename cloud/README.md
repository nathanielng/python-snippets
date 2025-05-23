# Cloud

## 1. S3

### 1.1 Downloading Files & Uploading to S3

The following code was generated using Amazon Q CLI

```python
import requests
import os

def download_file(url, destination=None):
    """
    Download a file from a URL to a local destination
    """
    if destination is None:
        destination = os.path.basename(urlparse(url).path)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Get the file size if available
        file_size = int(response.headers.get('content-length', 0))

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)

        with open(destination, 'wb') as file, tqdm(
            desc=destination,
            total=file_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False
```

```python
def extract_zip_file(zip_path, extract_to=None):
    """
    Extract a zip file to a specified directory

    Args:
        zip_path: Path to the zip file
        extract_to: Directory to extract to (defaults to same directory as zip file)

    Returns:
        bool: True if extraction was successful, False otherwise
    """
    try:
        # If extract_to is not specified, extract to the same directory as the zip file
        if extract_to is None:
            extract_to = os.path.dirname(os.path.abspath(zip_path))

            # If zip_path is just a filename with no directory, use current directory
            if not extract_to:
                extract_to = '.'

        # Create extraction directory if it doesn't exist
        os.makedirs(extract_to, exist_ok=True)

        # Open the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of files for progress tracking
            file_list = zip_ref.namelist()
            total_files = len(file_list)

            print(f"Extracting {total_files} files from {zip_path} to {extract_to}")

            # Extract all files with progress bar
            for file in tqdm(file_list, desc="Extracting"):
                zip_ref.extract(file, extract_to)

        print(f"Successfully extracted {total_files} files to {extract_to}")
        return True

    except zipfile.BadZipFile:
        print(f"Error: {zip_path} is not a valid zip file")
        return False
    except Exception as e:
        print(f"Error extracting zip file: {e}")
        return False
```

```python
def upload_directory(path, s3_bucket):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_to_upload = os.path.join(root, file)
            basename = os.path.basename(file_to_upload)
            if basename == ".DS_Store":
                print(f"Skipping file .DS_Store")
                continue
            print(f"uploading file {file_to_upload} to {bucket_name}")
            s3_client.upload_file(file_to_upload,s3_bucket,file)
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
