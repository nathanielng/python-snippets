import boto3
import datetime
import json

iam = boto3.client('iam')

# Trust policy
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "sagemaker.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

# Create policy
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": ["s3:ListBucket"],
            "Effect": "Allow",
            "Resource": ["arn:aws:s3:::sagemaker"]
        },
        {
            "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
            "Effect": "Allow",
            "Resource": ["arn:aws:s3:::sagemaker/*"]
        }
    ]
}

def check_if_role_exists(role_name):
    try:
        response = iam.get_role(RoleName=role_name)
        return True
    except iam.exceptions.NoSuchEntityException:
        return False

def check_if_policy_exists(policy_name):
    policy_arn = f'arn:aws:iam::aws:policy/root-task/{policy_name}'
    try:
        response = iam.get_policy(PolicyArn=policy_arn)
        return True
    except iam.exceptions.NoSuchEntityException:
        return False

def create_policy_if_not_exists(policy_name, policy_document):
    if not check_if_policy_exists(policy_name):
        return iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
    else:
        return None

def create_sagemaker_execution_role(role_name):
    role_response = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy)
    )
    print(json.dumps(role_response, indent=2, default=str))

    now = datetime.datetime.now()
    policy_name = 'SageMakerS3Policy-' + now.strftime("%Y%m")
    policy_response = create_policy_if_not_exists(policy_name, policy_document)
    if policy_response is None:
        print(f"Skipping policy creation because Policy {policy_name} already exists.")
    else:
        print(json.dumps(policy_response, indent=2, default=str))
    
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_response['Policy']['Arn']
    )
    
    # Attach SageMaker Full Access Policy
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
    )
    return {
        'role_response': role_response,
        'policy_response': policy_response
    }

def main():
    now = datetime.datetime.now()
    role_name = 'SageMakerExecutionRole-' + now.strftime("%Y%m")
    if check_if_role_exists(role_name):
        print(f"Role {role_name} already exists.")
        return

    responses = create_sagemaker_execution_role(role_name)
    role_response = responses['role_response']
    policy_response = responses['policy_response']
    print(f"Role ARN: {role_response['Role']['Arn']}")
    print(f"Policy ARN: {policy_response['Policy']['Arn']}")

if __name__ == "__main__":
    main()
