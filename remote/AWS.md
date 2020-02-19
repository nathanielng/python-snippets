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
