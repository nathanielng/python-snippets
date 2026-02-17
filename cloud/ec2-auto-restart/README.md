# EC2 Auto-Restart Lambda Function

Automatically restarts a stopped EC2 instance every 5 minutes using Lambda and EventBridge.

## Files

- `ec2_start_stop_lambda.py` - Lambda function code
- `deploy.py` - Deployment script (creates IAM role, Lambda, and EventBridge rule)

## Setup

1. Edit `deploy.py` and set:
   - `INSTANCE_ID` - Your EC2 instance ID
   - `REGIONS` - Comma-separated regions to manage (default: us-east-1,ap-southeast-1)
   - `REGION` - AWS region for Lambda deployment
   - `FUNCTION_NAME` - Lambda function name (optional)

2. Run deployment:
   ```bash
   python3 deploy.py
   ```

## Lambda Function Actions

The function supports three actions:

- `check_and_start` (default) - Starts instance only if stopped
- `start` - Force start the instance
- `stop` - Stop the instance

## Manual Invocation

```bash
# Check and start if stopped
aws lambda invoke --function-name ec2-restart-function \
  --payload '{"action":"check_and_start","instance_id":"i-XXXXXXXXXXXXX"}' response.json

# Force stop
aws lambda invoke --function-name ec2-restart-function \
  --payload '{"action":"stop","instance_id":"i-XXXXXXXXXXXXX"}' response.json
```

## Cleanup

```bash
aws events remove-targets --rule ec2-restart-every-5min --ids 1
aws events delete-rule --name ec2-restart-every-5min
aws lambda delete-function --function-name ec2-restart-function
aws iam delete-role-policy --role-name lambda-ec2-restart-role --policy-name ec2-restart-policy
aws iam delete-role --role-name lambda-ec2-restart-role
```
