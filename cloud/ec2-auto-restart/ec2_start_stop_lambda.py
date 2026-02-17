import boto3
import json
import os

def lambda_handler(event, context):
    """
    Manages EC2 instance state across multiple AWS regions.
    
    Args:
        event: Lambda event containing:
            - instance_id: EC2 instance ID (required)
            - action: 'check_and_start' (default), 'start', or 'stop'
            - regions: Comma-separated regions (default: 'us-east-1,ap-southeast-1')
        context: Lambda context object
    
    Returns:
        dict: Status code and results for each region
    """
    instance_id = event.get('instance_id') or os.environ.get('INSTANCE_ID')
    action = event.get('action', 'check_and_start')
    regions = event.get('regions') or os.environ.get('REGIONS', 'us-east-1,ap-southeast-1')
    
    if not instance_id:
        return {'statusCode': 400, 'body': 'instance_id required'}
    
    if isinstance(regions, str):
        regions = [r.strip() for r in regions.split(',')]
    
    results = []
    for region in regions:
        ec2 = boto3.client('ec2', region_name=region)
        
        try:
            response = ec2.describe_instances(InstanceIds=[instance_id])
            state = response['Reservations'][0]['Instances'][0]['State']['Name']
            
            if action == 'start' or (action == 'check_and_start' and state == 'stopped'):
                ec2.start_instances(InstanceIds=[instance_id])
                results.append(f'{region}: Started {instance_id}')
            elif action == 'stop':
                ec2.stop_instances(InstanceIds=[instance_id])
                results.append(f'{region}: Stopped {instance_id}')
            else:
                results.append(f'{region}: {instance_id} is {state}')
        except Exception as e:
            results.append(f'{region}: {str(e)}')
    
    return {'statusCode': 200, 'body': ', '.join(results)}
