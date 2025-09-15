#!/usr/bin/env python3

import argparse
import boto3
from typing import List


def check_and_update_lambda_runtimes_single_region(region: str, old_runtime: str, new_runtime: str):
    """
    Check Lambda functions in a single region for specific runtime and update if needed.
    
    Args:
        region: AWS region to check
        old_runtime: Runtime to check for (e.g., 'python3.9')
        new_runtime: Runtime to upgrade to (e.g., 'python3.12')
    """
    print(f"\n=== Checking region: {region} ===")
    
    try:
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Get all Lambda functions in the region
        paginator = lambda_client.get_paginator('list_functions')
        
        functions_to_update = []
        
        for page in paginator.paginate():
            for function in page['Functions']:
                function_name = function['FunctionName']
                runtime = function.get('Runtime', 'N/A')
                
                if runtime == old_runtime:
                    functions_to_update.append(function_name)
                    print(f"Found function '{function_name}' using {old_runtime}")
        
        if not functions_to_update:
            print(f"No functions found using {old_runtime}")
            return
        
        # Update functions with individual confirmation
        print(f"\nFound {len(functions_to_update)} functions to update:")
        
        for function_name in functions_to_update:
            confirm = input(f"Update '{function_name}' to {new_runtime}? (y/N): ")
            if confirm.lower() != 'y':
                print(f"⏭️  Skipped '{function_name}'")
                continue
            
            try:
                response = lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    Runtime=new_runtime
                )
                print(f"✅ Updated '{function_name}' to {new_runtime}")
                
            except Exception as e:
                print(f"❌ Failed to update '{function_name}': {str(e)}")
                
    except Exception as e:
        print(f"Error accessing region {region}: {str(e)}")


def check_and_update_lambda_runtimes(regions: List[str], old_runtime: str, new_runtime: str):
    """
    Check Lambda functions for specific runtime and update if needed.
    
    Args:
        regions: List of AWS regions to check
        old_runtime: Runtime to check for (e.g., 'python3.9')
        new_runtime: Runtime to upgrade to (e.g., 'python3.12')
    """
    for region in regions:
        check_and_update_lambda_runtimes_single_region(region, old_runtime, new_runtime)


def main(args):
    print(f"Checking Lambda functions for {args.old_runtime} runtime...")
    print(f"Will upgrade to {args.new_runtime} if confirmed")
    print(f"Regions to check: {', '.join(args.regions)}")
    
    check_and_update_lambda_runtimes(args.regions, args.old_runtime, args.new_runtime)
    print("\n=== Operation completed ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update Lambda function Python runtimes')
    parser.add_argument('--regions', '-r', nargs='+', 
                       default=['ap-southeast-1', 'us-west-2', 'us-east-1'],
                       help='AWS regions to check (default: ap-southeast-1 us-west-2 us-east-1)')
    parser.add_argument('--old-runtime', default='python3.9',
                       help='Runtime to check for (default: python3.9)')
    parser.add_argument('--new-runtime', default='python3.12',
                       help='Runtime to upgrade to (default: python3.12)')
    args = parser.parse_args()    
    main(args)
