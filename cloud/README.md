# Cloud

## 1. Lambda Functions

### 1.1 Invoke Lambda function

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


## 2. CloudFront

### 2.1 Invalidations

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


## 3. Webscraping README

### 3.1 Selenium Webdriver

#### 3.1.1 Links

- **Github**: https://github.com/SeleniumHQ/selenium
- **Documentation**: https://www.selenium.dev/selenium/docs/api/py/ (Python)

#### 3.1.2 Setup

1. **Safari** (Mac OS X): the web driver should already be located at `/usr/bin/safaridriver`, and may be enabled with the command `/usr/bin/safaridriver --enable`. In Safari, in the 'Develop' menu, enable 'Allow Remote Automation'.  The supported commands are listed [here](https://developer.apple.com/documentation/webkit/macos_webdriver_commands_for_safari_12_and_later)
2. **Chrome**: the chrome driver may be downloaded from [https://chromedriver.chromium.org](https://chromedriver.chromium.org)

```bash
pip install selenium
```


### 3.2 Mechanize

#### 3.2.1 Links

- **Github**: https://github.com/python-mechanize/mechanize
- **Documentation**: https://mechanize.readthedocs.io/en/latest/

#### 3.2.2 Setup

```bash
pip install mechanize
```
