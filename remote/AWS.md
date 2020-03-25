# AWS

## 1. S3 Buckets

### 1.1 List S3 Buckets

List all S3 buckets

```bash
aws s3 ls
```

Assign the last S3 bucket listed to an environment variable

```
S3_BUCKET=`aws s3 ls | tail -1 | cut -d ' ' -f 3`
```

### 1.2 List files in an S3 Bucket

```bash
aws s3 ls s3://$S3_BUCKET
```

### 1.3 Boto3 - Presigned URLs

- [Presigned URLs](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html)

## 2. EC2 Instances

Get help

```bash
aws ec2 help
```

Get information

```
aws ec2 describe-instances
aws ec2 describe-instance-status
aws ec2 describe-key-pairs
aws ec2 describe-security-groups
aws ec2 describe-vpcs
```
