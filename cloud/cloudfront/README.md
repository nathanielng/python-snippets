# CloudFront S3 Distribution Deployment

Automatically creates an S3 bucket and CloudFront distribution with Origin Access Control (OAC).

## Features

- Creates S3 bucket (or uses existing)
- Sets up Origin Access Control (OAC) for secure S3 access
- Creates CloudFront distribution with HTTPS redirect
- Configures bucket policy for CloudFront access
- Blocks public S3 access (CloudFront only)

## Setup

1. Edit `deploy.py` and set:
   - `BUCKET_NAME` - S3 bucket name (leave as `None` to auto-generate)
   - `REGION` - AWS region for S3 bucket (default: us-east-1)
   - `DISTRIBUTION_COMMENT` - Description for CloudFront distribution
   - `DEFAULT_TTL` - Default cache TTL in seconds (default: 0 = no cache)
   - `MIN_TTL` - Minimum cache TTL in seconds (default: 0)
   - `MAX_TTL` - Maximum cache TTL in seconds (default: 0)

2. Run deployment:
   ```bash
   python3 deploy.py
   ```

## Output

The script outputs:
- S3 bucket name
- CloudFront distribution ID
- CloudFront domain name
- CloudFront URL

## Upload Content

After deployment, upload files to S3:

```bash
aws s3 cp index.html s3://YOUR-BUCKET-NAME/
aws s3 sync ./website s3://YOUR-BUCKET-NAME/
```

## Access

Access your content via CloudFront URL:
```
https://d1234567890abc.cloudfront.net
```

## Cleanup

```bash
# Empty bucket
aws s3 rm s3://YOUR-BUCKET-NAME --recursive

# Delete bucket
aws s3 rb s3://YOUR-BUCKET-NAME

# Disable and delete distribution
aws cloudfront get-distribution-config --id DISTRIBUTION-ID > config.json
# Edit config.json: set "Enabled": false
aws cloudfront update-distribution --id DISTRIBUTION-ID --if-match ETAG --distribution-config file://config.json
# Wait for deployment, then delete
aws cloudfront delete-distribution --id DISTRIBUTION-ID --if-match ETAG
```

## Notes

- CloudFront deployment takes 15-20 minutes
- Default TTL is set to 0 seconds (no caching) - adjust in deploy.py if needed
- Default root object is `index.html`
- HTTPS is enforced (HTTP redirects to HTTPS)
