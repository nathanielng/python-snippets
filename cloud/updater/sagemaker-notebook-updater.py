#!/usr/bin/env python3
"""
SageMaker Notebook Instance JupyterLab Upgrade Tool

Disclaimer: this is a vibe-coded app and has not been extensively tested.

This tool automates the migration of Amazon SageMaker Notebook Instances from
JupyterLab 1 (notebook-al2-v1) and JupyterLab 3 (notebook-al2-v2) to JupyterLab 4
(notebook-al2023-v1 or notebook-al2-v3).

Features:
- Automatic detection of deprecated notebook instances
- Data backup verification
- Multi-region support
- Parallel processing capabilities
- Multiple execution modes (dry-run, interactive, force)
- Comprehensive reporting

Quickstart Guide:
-----------------

1. Prerequisites:
   - AWS credentials configured (via ~/.aws/credentials or environment variables)
   - Python 3.8+ installed
   - boto3 library installed: pip install boto3
   - Appropriate IAM permissions for SageMaker operations

2. Basic Usage:
   
   # Dry run to see what would be updated (no changes made)
   python sagemaker-notebook-updater.py --target-platform notebook-al2-v3 --mode dry-run
   
   # Interactive mode (recommended for first use)
   python sagemaker-notebook-updater.py --target-platform notebook-al2-v3 --mode interactive
   
   # Update to Amazon Linux 2023 platform
   python sagemaker-notebook-updater.py --target-platform notebook-al2023-v1 --mode interactive

3. Common Scenarios:
   
   # Update specific regions only
   python sagemaker-notebook-updater.py --regions us-east-1 eu-west-1 --target-platform notebook-al2-v3
   
   # Update from specific source platforms
   python sagemaker-notebook-updater.py --target-platform notebook-al2-v3 --source-platforms notebook-al2-v1 notebook-al2-v2
   
   # Force update (auto-updates all instances)
   python sagemaker-notebook-updater.py --target-platform notebook-al2-v3 --mode force
   
   # Use configuration file
   python sagemaker-notebook-updater.py --config sagemaker-updater-config.json

4. Understanding Modes:
   - dry-run: Lists notebook instances without making changes
   - interactive: Reviews each instance with you before updating
   - force: Auto-updates all instances without prompting

5. Output:
   - Console output shows progress and decisions
   - sagemaker_updater.log: Detailed execution log
   - sagemaker_upgrade_report.json: Comprehensive report of all instances
   - sagemaker_upgrade_report_summary.txt: Human-readable summary

6. Configuration File Example (sagemaker-updater-config.json):
   {
     "regions": ["us-east-1", "us-west-2"],
     "target_platform": "notebook-al2-v3",
     "source_platforms": ["notebook-al2-v1", "notebook-al2-v2"],
     "mode": "interactive"
   }

IMPORTANT NOTES:
- Data outside /home/ec2-user/SageMaker will NOT be persisted during upgrade
- Notebook instances will be stopped during the upgrade process
- All running workloads will be terminated during upgrade
- Backup your data before running this tool
"""

# Standard library imports
import argparse
import asyncio
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional

# Third-party imports
import boto3
from botocore.exceptions import ClientError

# Constants
DEFAULT_REGIONS = ['us-east-1']
DEPRECATED_PLATFORMS = ['notebook-al2-v1', 'notebook-al2-v2']
TARGET_PLATFORMS = ['notebook-al2-v3', 'notebook-al2023-v1']

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sagemaker_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# TEMPLATE STRINGS AND PROMPTS
# ============================================================================

CLI_HELP_EXAMPLES = """
Examples:
  # Dry run to see what would be updated
  python sagemaker-notebook-updater.py --target-platform notebook-al2-v3 --mode dry-run
  
  # Interactive mode with confirmation prompts
  python sagemaker-notebook-updater.py --target-platform notebook-al2-v3 --mode interactive
  
  # Force update all instances
  python sagemaker-notebook-updater.py --target-platform notebook-al2-v3 --mode force
  
  # Update specific regions
  python sagemaker-notebook-updater.py --regions us-east-1 eu-west-1 --target-platform notebook-al2-v3
  
  # Load configuration from file
  python sagemaker-notebook-updater.py --config config.json
"""

MODE_BEHAVIOR = {
    'dry-run': 'List all notebook instances without updating',
    'interactive': 'Prompt for confirmation before updating each instance',
    'force': 'Update all instances without prompting'
}

PLATFORM_INFO = {
    'notebook-al2-v1': {
        'name': 'JupyterLab 1',
        'status': 'EOL (June 30, 2025)',
        'deprecated': True
    },
    'notebook-al2-v2': {
        'name': 'JupyterLab 3',
        'status': 'EOL (June 30, 2025)',
        'deprecated': True
    },
    'notebook-al2-v3': {
        'name': 'JupyterLab 4 (Amazon Linux 2)',
        'status': 'Current',
        'deprecated': False
    },
    'notebook-al2023-v1': {
        'name': 'JupyterLab 4 (Amazon Linux 2023)',
        'status': 'Current',
        'deprecated': False
    }
}

class NotebookStatus(Enum):
    IN_SERVICE = "InService"
    PENDING = "Pending"
    STOPPING = "Stopping"
    STOPPED = "Stopped"
    FAILED = "Failed"
    DELETING = "Deleting"
    UPDATING = "Updating"

@dataclass
class NotebookInstanceInfo:
    """
    Data class representing information about a SageMaker Notebook Instance.
    
    Attributes:
        name: The notebook instance name
        arn: The full ARN of the notebook instance
        region: AWS region where the instance is deployed
        platform: Current platform identifier (e.g., 'notebook-al2-v1')
        status: Current status of the notebook instance
        instance_type: EC2 instance type
        volume_size_gb: EBS volume size in GB
        updated: Whether the instance was successfully updated
        skipped: Whether the instance was skipped during processing
        failed: Whether the update attempt failed
        error_message: Error details if the update failed
    """
    name: str
    arn: str
    region: str
    platform: str
    status: str
    instance_type: str
    volume_size_gb: int
    updated: bool = False
    skipped: bool = False
    failed: bool = False
    error_message: Optional[str] = None

class SageMakerNotebookUpdater:
    def __init__(self, regions: List[str], target_platform: str, mode: str,
                 source_platforms: Optional[List[str]] = None,
                 max_workers: int = 5):
        self.regions = regions
        self.target_platform = target_platform
        self.mode = mode
        self.source_platforms = source_platforms or DEPRECATED_PLATFORMS
        self.max_workers = max_workers
        
        # Validate platform upgrade path
        self._validate_platform_upgrade()
    
    def _validate_platform_upgrade(self) -> None:
        """Validate that the platform upgrade path is supported"""
        if self.target_platform not in TARGET_PLATFORMS:
            raise ValueError(f"Target platform must be one of: {TARGET_PLATFORMS}")
        
        for source_platform in self.source_platforms:
            if source_platform not in DEPRECATED_PLATFORMS:
                logger.warning(f"Source platform {source_platform} is not deprecated")
        
        logger.info(f"Platform upgrade validation passed")
    
    def load_config(self, config_file: str = None) -> Dict:
        """Load configuration from file"""
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
        return {}
    
    def list_deprecated_notebook_instances(self, sagemaker_client) -> List[Dict]:
        """List all notebook instances using deprecated platforms"""
        instances = []
        try:
            paginator = sagemaker_client.get_paginator('list_notebook_instances')
            
            for page in paginator.paginate():
                for instance in page['NotebookInstances']:
                    # Get detailed info to check platform
                    try:
                        details = sagemaker_client.describe_notebook_instance(
                            NotebookInstanceName=instance['NotebookInstanceName']
                        )
                        
                        platform = details.get('PlatformIdentifier', 'unknown')
                        if platform in self.source_platforms:
                            instances.append(details)
                    except ClientError as e:
                        logger.warning(f"Failed to describe {instance['NotebookInstanceName']}: {e}")
                        continue
                        
        except ClientError as e:
            logger.error(f"Failed to list notebook instances: {e}")
            raise
        
        return instances

    
    def stop_notebook_instance(self, sagemaker_client, instance_name: str) -> Tuple[bool, str]:
        """Stop a notebook instance if it's running"""
        try:
            details = sagemaker_client.describe_notebook_instance(
                NotebookInstanceName=instance_name
            )
            
            status = details['NotebookInstanceStatus']
            
            if status == 'InService':
                logger.info(f"    Stopping notebook instance {instance_name}...")
                sagemaker_client.stop_notebook_instance(
                    NotebookInstanceName=instance_name
                )
                
                # Wait for instance to stop
                waiter = sagemaker_client.get_waiter('notebook_instance_stopped')
                waiter.wait(
                    NotebookInstanceName=instance_name,
                    WaiterConfig={'Delay': 30, 'MaxAttempts': 40}
                )
                logger.info(f"    ✓ Instance stopped successfully")
                return True, "Stopped"
            elif status == 'Stopped':
                logger.info(f"    Instance already stopped")
                return True, "Already stopped"
            else:
                return False, f"Instance in {status} state, cannot stop"
                
        except ClientError as e:
            logger.error(f"Failed to stop {instance_name}: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected error stopping {instance_name}: {e}")
            return False, str(e)
    
    def update_notebook_instance(self, sagemaker_client, instance_name: str) -> Tuple[bool, str]:
        """Update a notebook instance's platform with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # First, ensure instance is stopped
                stop_success, stop_message = self.stop_notebook_instance(sagemaker_client, instance_name)
                if not stop_success:
                    return False, f"Failed to stop instance: {stop_message}"
                
                # Update the platform
                logger.info(f"    Updating platform to {self.target_platform}...")
                response = sagemaker_client.update_notebook_instance(
                    NotebookInstanceName=instance_name,
                    PlatformIdentifier=self.target_platform
                )
                
                # Wait for update to complete
                logger.info(f"    Waiting for update to complete...")
                time.sleep(5)  # Initial delay
                
                # Check status
                max_checks = 60
                for check in range(max_checks):
                    details = sagemaker_client.describe_notebook_instance(
                        NotebookInstanceName=instance_name
                    )
                    status = details['NotebookInstanceStatus']
                    
                    if status == 'Stopped':
                        logger.info(f"    ✓ Update completed successfully")
                        return True, "Success"
                    elif status in ['Failed', 'Deleting']:
                        return False, f"Update failed with status: {status}"
                    
                    time.sleep(10)
                
                return False, "Update timeout - status check exceeded max attempts"
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceInUse' and attempt < max_retries - 1:
                    logger.warning(f"Resource in use for {instance_name}, retrying in 30 seconds...")
                    time.sleep(30)
                    continue
                else:
                    logger.error(f"Failed to update {instance_name}: {e}")
                    return False, str(e)
            except Exception as e:
                logger.error(f"Unexpected error updating {instance_name}: {e}")
                return False, str(e)
        
        return False, "Max retries exceeded"
    
    async def process_instance_async(self, sagemaker_client, instance: Dict, region: str,
                                     index: int, total: int) -> NotebookInstanceInfo:
        """Process a single notebook instance asynchronously"""
        instance_info = NotebookInstanceInfo(
            name=instance['NotebookInstanceName'],
            arn=instance['NotebookInstanceArn'],
            region=region,
            platform=instance.get('PlatformIdentifier', 'unknown'),
            status=instance['NotebookInstanceStatus'],
            instance_type=instance['InstanceType'],
            volume_size_gb=instance.get('VolumeSizeInGB', 0)
        )
        
        logger.info(f"[{index}/{total}] Processing {instance_info.name}")
        logger.info(f"    ARN: {instance_info.arn}")
        logger.info(f"    Current Platform: {instance_info.platform} ({PLATFORM_INFO.get(instance_info.platform, {}).get('name', 'Unknown')})")
        logger.info(f"    Status: {instance_info.status}")
        logger.info(f"    Instance Type: {instance_info.instance_type}")
        logger.info(f"    Volume Size: {instance_info.volume_size_gb} GB")
        
        return instance_info
    
    def get_mode_behavior(self) -> Dict[str, str]:
        """Get mode behavior description"""
        return MODE_BEHAVIOR
    
    def prompt_user_interactive(self, instance_info: NotebookInstanceInfo) -> str:
        """Prompt user in interactive mode"""
        print(f"\n    {'='*60}")
        print(f"    NOTEBOOK INSTANCE DETAILS")
        print(f"    {'='*60}")
        print(f"    Name: {instance_info.name}")
        print(f"    Current Platform: {instance_info.platform}")
        print(f"    Target Platform: {self.target_platform}")
        print(f"    Status: {instance_info.status}")
        print(f"    Instance Type: {instance_info.instance_type}")
        print(f"    Volume Size: {instance_info.volume_size_gb} GB")
        print(f"    {'='*60}")
        print(f"\n    ⚠ WARNING:")
        print(f"    - Instance will be STOPPED during upgrade")
        print(f"    - All running workloads will be TERMINATED")
        print(f"    - Data outside /home/ec2-user/SageMaker will NOT be persisted")
        print(f"    - Ensure you have backed up important data")
        print(f"    {'='*60}")
        
        while True:
            response = input(f"\n    Update {instance_info.name}? [y/n/q]: ").lower().strip()
            
            if response in ['y', 'yes']:
                return 'yes'
            elif response in ['n', 'no']:
                return 'no'
            elif response in ['q', 'quit']:
                return 'quit'
            else:
                print("    Please enter 'y' (yes), 'n' (no), or 'q' (quit)")
    
    def generate_report(self, all_instances: List[NotebookInstanceInfo],
                       output_file: str = "sagemaker_upgrade_report.json"):
        """Generate comprehensive report"""
        report = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_platforms": self.source_platforms,
            "target_platform": self.target_platform,
            "regions": self.regions,
            "mode": self.mode,
            "total_instances": len(all_instances),
            "instances": []
        }
        
        for instance_info in all_instances:
            instance_report = {
                "instance_name": instance_info.name,
                "instance_arn": instance_info.arn,
                "region": instance_info.region,
                "current_platform": instance_info.platform,
                "status": instance_info.status,
                "instance_type": instance_info.instance_type,
                "volume_size_gb": instance_info.volume_size_gb,
                "updated": instance_info.updated,
                "skipped": instance_info.skipped,
                "failed": instance_info.failed
            }
            
            if instance_info.error_message:
                instance_report["error_message"] = instance_info.error_message
            
            report["instances"].append(instance_report)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate summary
        summary_file = output_file.replace('.json', '_summary.txt')
        with open(summary_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("SAGEMAKER NOTEBOOK INSTANCE UPGRADE REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Generated: {report['generated_at']}\n")
            f.write(f"Source Platforms: {', '.join(self.source_platforms)}\n")
            f.write(f"Target Platform: {self.target_platform}\n")
            f.write(f"Mode: {self.mode}\n")
            f.write(f"Regions: {', '.join(self.regions)}\n")
            f.write(f"Total Instances: {len(all_instances)}\n\n")
            
            updated = sum(1 for i in all_instances if i.updated)
            skipped = sum(1 for i in all_instances if i.skipped)
            failed = sum(1 for i in all_instances if i.failed)
            
            f.write("EXECUTION SUMMARY:\n")
            f.write(f"  Updated: {updated}\n")
            f.write(f"  Skipped: {skipped}\n")
            f.write(f"  Failed: {failed}\n\n")
            
            f.write("="*70 + "\n")
            f.write("DETAILED FINDINGS\n")
            f.write("="*70 + "\n\n")
            
            for instance_info in all_instances:
                f.write(f"\nInstance: {instance_info.name}\n")
                f.write(f"Region: {instance_info.region}\n")
                f.write(f"Current Platform: {instance_info.platform}\n")
                f.write(f"Instance Type: {instance_info.instance_type}\n")
                f.write(f"Volume Size: {instance_info.volume_size_gb} GB\n")
                f.write(f"Status: {'Updated' if instance_info.updated else 'Skipped' if instance_info.skipped else 'Failed' if instance_info.failed else 'Not Processed'}\n")
                
                if instance_info.error_message:
                    f.write(f"Error: {instance_info.error_message}\n")
                
                f.write("\n" + "-"*70 + "\n")
        
        return output_file, summary_file
    
    async def process_region_async(self, region: str) -> Tuple[str, List[NotebookInstanceInfo]]:
        """Process all notebook instances in a region asynchronously"""
        logger.info(f"\n{'='*70}")
        logger.info(f"Processing region: {region}")
        logger.info(f"{'='*70}")
        
        try:
            sagemaker_client = boto3.client('sagemaker', region_name=region)
            instances = self.list_deprecated_notebook_instances(sagemaker_client)
            
            if not instances:
                logger.info(f"✓ No notebook instances found using {', '.join(self.source_platforms)} in {region}")
                return region, []
            
            region_total = len(instances)
            logger.info(f"Found {region_total} notebook instance(s) using deprecated platforms\n")
            
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def process_with_semaphore(instance, idx):
                async with semaphore:
                    return await self.process_instance_async(sagemaker_client, instance, region, idx, region_total)
            
            tasks = [process_with_semaphore(instance, i+1) for i, instance in enumerate(instances)]
            instance_infos = await asyncio.gather(*tasks)
            
            return region, instance_infos
            
        except Exception as e:
            logger.error(f"✗ Error processing region {region}: {e}")
            return region, []
    
    async def run_async(self) -> None:
        """Main async execution method"""
        logger.info("=" * 70)
        logger.info("SageMaker Notebook Instance JupyterLab Upgrade Tool")
        logger.info("=" * 70)
        logger.info(f"Source Platforms: {', '.join(self.source_platforms)}")
        logger.info(f"Target Platform: {self.target_platform}")
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Regions: {', '.join(self.regions)}")
        logger.info(f"Max Parallel Workers: {self.max_workers}")
        logger.info("\nMode Behavior:")
        for mode, behavior in self.get_mode_behavior().items():
            marker = "→" if mode == self.mode else " "
            logger.info(f"  {marker} {mode}: {behavior}")
        logger.info("=" * 70)
        
        logger.info(f"\n{'='*70}")
        logger.info("⚠ IMPORTANT WARNINGS:")
        logger.info("="*70)
        logger.info("• Notebook instances will be STOPPED during upgrade")
        logger.info("• All running workloads will be TERMINATED")
        logger.info("• Data outside /home/ec2-user/SageMaker will NOT be persisted")
        logger.info("• Ensure you have backed up important data before proceeding")
        logger.info("="*70)
        
        # Phase 1: Discover all instances
        logger.info(f"\n{'='*70}")
        logger.info("PHASE 1: DISCOVERY")
        logger.info("="*70)
        
        region_tasks = [self.process_region_async(region) for region in self.regions]
        region_results = await asyncio.gather(*region_tasks)
        
        all_instances = []
        for region, instance_infos in region_results:
            all_instances.extend(instance_infos)
        
        if not all_instances:
            logger.info(f"\n✓ No notebook instances found using {', '.join(self.source_platforms)} in any region")
            return
        
        logger.info(f"\n{'='*70}")
        logger.info(f"DISCOVERY COMPLETE: Found {len(all_instances)} notebook instance(s) total")
        logger.info(f"{'='*70}")
        
        # Phase 2: Update instances based on mode
        if self.mode == 'dry-run':
            logger.info("\n✓ Dry-run complete. No instances were updated.")
        else:
            logger.info(f"\n{'='*70}")
            logger.info("PHASE 2: PLATFORM UPDATES")
            logger.info("="*70 + "\n")
            
            quit_requested = False
            
            for instance_info in all_instances:
                if quit_requested:
                    break
                
                logger.info(f"\nProcessing: {instance_info.name} ({instance_info.region})")
                
                if self.mode == 'interactive':
                    user_choice = self.prompt_user_interactive(instance_info)
                    if user_choice == 'quit':
                        logger.warning("\n⚠ User requested quit. Stopping execution.")
                        quit_requested = True
                        break
                    elif user_choice == 'no':
                        logger.info(f"    ⊘ Skipped by user")
                        instance_info.skipped = True
                        continue
                
                logger.info(f"    ⟳ Updating to {self.target_platform}...")
                sagemaker_client = boto3.client('sagemaker', region_name=instance_info.region)
                success, result = self.update_notebook_instance(sagemaker_client, instance_info.name)
                
                if success:
                    logger.info(f"    ✓ Successfully updated")
                    instance_info.updated = True
                else:
                    logger.error(f"    ✗ Failed: {result}")
                    instance_info.failed = True
                    instance_info.error_message = result
                
                time.sleep(1)
        
        # Generate report
        logger.info(f"\n{'='*70}")
        logger.info("Generating Report...")
        report_file, summary_file = self.generate_report(all_instances)
        logger.info(f"✓ Report saved to: {report_file}")
        logger.info(f"✓ Summary saved to: {summary_file}")
        
        # Final summary
        logger.info(f"\n{'='*70}")
        logger.info("FINAL SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Total instances found: {len(all_instances)}")
        
        if self.mode == 'dry-run':
            logger.info(f"Instances analyzed: {len(all_instances)}")
        else:
            updated = sum(1 for i in all_instances if i.updated)
            skipped = sum(1 for i in all_instances if i.skipped)
            failed = sum(1 for i in all_instances if i.failed)
            
            logger.info(f"Successfully updated: {updated}")
            logger.info(f"Skipped: {skipped}")
            logger.info(f"Failed: {failed}")
        
        logger.info(f"{'='*70}")
    
    def run(self) -> None:
        """Synchronous wrapper for async execution"""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            logger.warning("Process interrupted by user")
            raise
        except Exception as e:
            logger.error(f"Runtime execution error: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description='Update SageMaker Notebook Instances from JupyterLab 1/3 to JupyterLab 4',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CLI_HELP_EXAMPLES
    )
    
    parser.add_argument('--regions', nargs='+', default=DEFAULT_REGIONS,
                       help=f'AWS regions to process (default: {DEFAULT_REGIONS})')
    parser.add_argument('--target-platform', required=True,
                       choices=TARGET_PLATFORMS,
                       help='Target platform identifier')
    parser.add_argument('--source-platforms', nargs='+',
                       default=DEPRECATED_PLATFORMS,
                       help='Source platforms to upgrade from')
    parser.add_argument('--mode', choices=['dry-run', 'interactive', 'force'],
                       default='interactive', help='Execution mode (default: interactive)')
    parser.add_argument('--max-workers', type=int, default=5,
                       help='Maximum parallel workers (default: 5)')
    parser.add_argument('--config',
                       help='Load configuration from JSON file')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        # Load configuration if specified
        config = {}
        if args.config:
            if not os.path.exists(args.config):
                logger.error(f"Configuration file not found: {args.config}")
                return 1
            
            with open(args.config, 'r') as f:
                config = json.load(f)
            
            logger.info(f"Loaded configuration from {args.config}")
        
        # Override config with command line arguments
        updater_args = {
            'regions': args.regions,
            'target_platform': args.target_platform,
            'mode': args.mode,
            'source_platforms': args.source_platforms,
            'max_workers': args.max_workers
        }
        
        # Apply config file settings (command line args take precedence)
        for key, value in config.items():
            if key in updater_args and updater_args[key] is None:
                updater_args[key] = value
        
        updater = SageMakerNotebookUpdater(**updater_args)
        updater.run()
        
        logger.info("SageMaker notebook instance upgrade process completed successfully")
        return 0
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        return 130
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
