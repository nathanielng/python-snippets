
#!/usr/bin/env python3
"""
Enhanced Lambda Runtime Update Tool with AI Code Review and Parallel Processing

Disclaimer: this app was vibe coded and has not been tested extensively

This tool provides automated AWS Lambda function runtime upgrades with AI-powered
code analysis using AWS Bedrock. It supports both Node.js and Python runtimes
with parallel processing capabilities and comprehensive reporting.

Features:
- Multi-runtime support (Node.js and Python)
- AI-powered code compatibility analysis
- Parallel processing across regions and functions
- Multiple execution modes (dry-run, interactive, force)
- Comprehensive JSON and text reporting
- Security-focused code handling

Quickstart Guide:
-----------------

1. Prerequisites:
   - AWS credentials configured (via ~/.aws/credentials or environment variables)
   - Python 3.8+ installed
   - boto3 library installed: pip install boto3
   - AWS Bedrock access enabled in your account (for AI review features)

2. Basic Usage:
   
   # Dry run to see what would be updated (no changes made)
   python lambda-updater-multi.py --target-runtime nodejs22.x --mode dry-run
   
   # Interactive mode with AI review (recommended for first use)
   python lambda-updater-multi.py --target-runtime nodejs22.x --mode interactive --ai-review
   
   # Update Python functions from 3.9 to 3.13
   python lambda-updater-multi.py --target-runtime python3.13 --mode interactive --ai-review

3. Common Scenarios:
   
   # Update specific regions only
   python lambda-updater-multi.py --regions us-east-1 eu-west-1 --target-runtime nodejs22.x --ai-review
   
   # Update from specific source runtimes
   python lambda-updater-multi.py --target-runtime python3.13 --source-runtimes python3.9 python3.8 --ai-review
   
   # Force update (auto-updates safe functions, prompts for risky ones)
   python lambda-updater-multi.py --target-runtime nodejs22.x --mode force --ai-review
   
   # Use configuration file
   python lambda-updater-multi.py --config lambda-updater-config.json

4. Understanding Modes:
   - dry-run: Lists functions and shows AI analysis without making changes
   - interactive: Reviews each function with you before updating
   - force: Auto-updates safe functions, skips problematic ones, prompts for uncertain cases

5. Output:
   - Console output shows progress and decisions
   - lambda_updater.log: Detailed execution log
   - lambda_upgrade_report.json: Comprehensive report of all functions analyzed
   - lambda_upgrade_report.txt: Human-readable summary

6. Configuration File Example (lambda-updater-config.json):
   {
     "regions": ["us-east-1", "us-west-2"],
     "target_runtime": "nodejs22.x",
     "source_runtimes": ["nodejs20.x", "nodejs18.x"],
     "mode": "interactive",
     "ai_review": true
   }

Lambda_Runtime_Update_Tool_with_Multi_Runtime_Support_2025_12_14T08_49_19.py
"""

# Standard library imports
import argparse
import asyncio
import io
import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
import zipfile

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional

# Third-party imports
import boto3
from botocore.exceptions import ClientError

# Constants
DEFAULT_REGIONS = ['us-east-1', 'us-west-2', 'ap-southeast-1']
MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50MB
DOWNLOAD_TIMEOUT = 30  # seconds
MAX_FILE_SIZE_FOR_ANALYSIS = 1024 * 1024  # 1MB per file

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lambda_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# TEMPLATE STRINGS AND PROMPTS
# ============================================================================

NODEJS_ANALYSIS_GUIDANCE = """
Focus on Node.js runtime-specific issues, especially:
- Callback vs Promise/async-await patterns (critical for Node.js 22+)
- Deprecated Node.js APIs
- AWS SDK v2 vs v3 usage
- Module system (CommonJS vs ES modules)
- Changes in error handling and unresolved promises
"""

PYTHON_ANALYSIS_GUIDANCE = """
Focus on Python runtime-specific issues, especially:
- Deprecated Python standard library functions
- Changes in async/await behavior
- Type hints and annotations compatibility
- Package compatibility (especially boto3/botocore versions)
- Changes in exception handling
- Differences in standard library modules
"""

BEDROCK_ANALYSIS_PROMPT_TEMPLATE = """You are an expert AWS Lambda developer analyzing {runtime_type} code for runtime migration compatibility.

Function Name: {function_name}
Current Runtime: {current_runtime}
Target Runtime: {target_runtime}

Code to analyze:
{code_context}

Please analyze this Lambda function code and identify:

1. **Critical Issues**: Problems that will cause the function to fail (e.g., deprecated APIs, breaking changes)
2. **Warnings**: Potential issues that may cause problems (e.g., deprecated features, performance concerns)
3. **Recommendations**: Best practices and improvements for the new runtime
4. **Dependencies**: Any package dependencies that may need updates

{runtime_specific_guidance}

Provide your analysis in the following JSON format:
{{
  "critical_issues": [
    {{"issue": "description", "location": "file:line", "fix": "suggested fix"}}
  ],
  "warnings": [
    {{"issue": "description", "location": "file:line", "recommendation": "suggestion"}}
  ],
  "recommendations": ["recommendation1", "recommendation2"],
  "dependencies_to_check": ["package1", "package2"],
  "overall_assessment": "SAFE_TO_UPGRADE | NEEDS_CHANGES | REQUIRES_TESTING",
  "summary": "brief summary of findings"
}}
"""

CLI_HELP_EXAMPLES = """
Examples:
  # Update Node.js functions from 20.x to 22.x with AI review
  python lambda-updater-multi.py --target-runtime nodejs22.x --mode interactive --ai-review
  
  # Dry run for Python functions
  python lambda-updater-multi.py --target-runtime python3.13 --mode dry-run --ai-review
  
  # Force update without AI review
  python lambda-updater-multi.py --target-runtime nodejs22.x --mode force
  
  # Update specific regions with custom source runtimes
  python lambda-updater-multi.py --regions us-east-1 eu-west-1 --target-runtime python3.13 --source-runtimes python3.9 python3.8 --ai-review
  
  # Load configuration from file
  python lambda-updater-multi.py --config config.json
"""

MODE_BEHAVIOR_WITH_AI = {
    'dry-run': 'List all functions and perform AI analysis without updating',
    'interactive': 'AI analyzes code first, then prompts with recommendation for each function',
    'force': 'AI analyzes code; auto-updates SAFE functions, auto-skips NEEDS_CHANGES, prompts for REQUIRES_TESTING'
}

MODE_BEHAVIOR_WITHOUT_AI = {
    'dry-run': 'List all functions without updating',
    'interactive': 'Prompt for confirmation before updating each function',
    'force': 'Update all functions without prompting'
}

# Runtime mappings
RUNTIME_MAPPINGS = {
    'nodejs': {
        'deprecated': ['nodejs20.x', 'nodejs18.x', 'nodejs16.x', 'nodejs14.x'],
        'latest': 'nodejs24.x',
        'recommended': 'nodejs22.x',
        'file_extensions': ['.js', '.mjs', '.cjs']
    },
    'python': {
        'deprecated': ['python3.9', 'python3.8', 'python3.7'],
        'latest': 'python3.14',
        'recommended': 'python3.13',
        'file_extensions': ['.py']
    }
}

class AIAssessment(Enum):
    SAFE_TO_UPGRADE = "SAFE_TO_UPGRADE"
    NEEDS_CHANGES = "NEEDS_CHANGES"
    REQUIRES_TESTING = "REQUIRES_TESTING"
    ERROR = "ERROR"
    NOT_ANALYZED = "NOT_ANALYZED"

@dataclass
class FunctionInfo:
    """
    Data class representing information about a Lambda function during the upgrade process.
    
    The @dataclass decorator automatically generates common methods like __init__, __repr__, 
    and __eq__ based on the field definitions, reducing boilerplate code.
    
    Attributes:
        name: The Lambda function name
        arn: The full ARN (Amazon Resource Name) of the function
        region: AWS region where the function is deployed
        runtime: Current runtime version (e.g., 'nodejs20.x', 'python3.9')
        code_files: Dictionary mapping file names to their source code content
        ai_analysis: Results from Bedrock AI analysis of the function code
        assessment: AI's overall assessment of upgrade safety
        updated: Whether the function was successfully updated
        skipped: Whether the function was skipped during processing
        failed: Whether the update attempt failed
        error_message: Error details if the update failed
    """
    name: str
    arn: str
    region: str
    runtime: str
    code_files: Optional[Dict[str, str]] = None
    ai_analysis: Optional[Dict] = None
    assessment: AIAssessment = AIAssessment.NOT_ANALYZED
    updated: bool = False
    skipped: bool = False
    failed: bool = False
    error_message: Optional[str] = None

class LambdaRuntimeUpdater:
    def __init__(self, regions: List[str], target_runtime: str, mode: str, 
                 source_runtimes: Optional[List[str]] = None,
                 ai_review: bool = False, 
                 bedrock_model: str = 'anthropic.claude-3-5-sonnet-20241022-v2:0',
                 max_workers: int = 5):
        self.regions = regions
        self.target_runtime = target_runtime
        self.mode = mode
        self.source_runtimes = source_runtimes or self._get_default_source_runtimes()
        self.ai_review = ai_review
        self.bedrock_model = bedrock_model
        self.max_workers = max_workers
        self.bedrock_client = None
        
        # Validate runtime upgrade path
        self._validate_runtime_upgrade()
        
        # Determine runtime type
        self.runtime_type = self._detect_runtime_type()
        
        if ai_review:
            self.bedrock_client = self._initialize_bedrock_client()
    
    def _initialize_bedrock_client(self):
        """Initialize Bedrock client with error handling"""
        try:
            return boto3.client('bedrock-runtime', region_name='us-east-1')
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def _validate_runtime_upgrade(self) -> None:
        """Validate that the runtime upgrade path is supported"""
        target_type = self._detect_runtime_type_from_string(self.target_runtime)
        
        for source_runtime in self.source_runtimes or []:
            source_type = self._detect_runtime_type_from_string(source_runtime)
            if source_type != target_type:
                raise ValueError(f"Cannot upgrade from {source_type} to {target_type}")
        
        logger.info(f"Runtime upgrade validation passed: {target_type}")
    
    def _detect_runtime_type_from_string(self, runtime: str) -> str:
        """Detect runtime type from runtime string"""
        if runtime.startswith('nodejs'):
            return 'nodejs'
        elif runtime.startswith('python'):
            return 'python'
        else:
            raise ValueError(f"Unsupported runtime: {runtime}")
    
    def _detect_runtime_type(self) -> str:
        """Detect whether we're working with Node.js or Python runtimes"""
        return self._detect_runtime_type_from_string(self.target_runtime)
    
    def _get_default_source_runtimes(self) -> List[str]:
        """Get default source runtimes based on target runtime"""
        if self.target_runtime.startswith('nodejs'):
            return ['nodejs20.x']
        elif self.target_runtime.startswith('python'):
            return ['python3.9']
        return []
    
    def load_config(self, config_file: str = None) -> Dict:
        """Load configuration from file"""
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
        return {}
    
    def list_deprecated_functions(self, lambda_client) -> List[Dict]:
        """List all functions using deprecated runtimes"""
        functions = []
        try:
            paginator = lambda_client.get_paginator('list_functions')
            
            for page in paginator.paginate():
                for function in page['Functions']:
                    if function.get('Runtime') in self.source_runtimes:
                        functions.append(function)
        except ClientError as e:
            logger.error(f"Failed to list functions: {e}")
            raise
        
        return functions
    
    def get_function_code(self, lambda_client, function_name: str) -> Optional[Dict[str, str]]:
        """Download and extract Lambda function code with security measures"""
        try:
            response = lambda_client.get_function(FunctionName=function_name)
            code_location = response['Code']['Location']
            
            # Download with timeout and size limits
            request = urllib.request.Request(code_location)
            with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT) as response:
                # Read with size limit to prevent memory issues
                zip_data = response.read(MAX_DOWNLOAD_SIZE)
            
            code_files = {}
            file_extensions = RUNTIME_MAPPINGS[self.runtime_type]['file_extensions']
            
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
                for file_info in zip_ref.filelist:
                    # Security check: prevent path traversal
                    if '..' in file_info.filename or file_info.filename.startswith('/'):
                        logger.warning(f"Skipping suspicious file path: {file_info.filename}")
                        continue
                    
                    # Check file size
                    if file_info.file_size > MAX_FILE_SIZE_FOR_ANALYSIS:
                        logger.warning(f"Skipping large file: {file_info.filename} ({file_info.file_size} bytes)")
                        continue
                    
                    if any(file_info.filename.endswith(ext) for ext in file_extensions):
                        try:
                            content = zip_ref.read(file_info.filename).decode('utf-8')
                            code_files[file_info.filename] = content
                        except UnicodeDecodeError:
                            logger.warning(f"Skipping binary file: {file_info.filename}")
                            continue
                        except Exception as e:
                            logger.warning(f"Error reading file {file_info.filename}: {e}")
                            continue
            
            return code_files if code_files else None
            
        except urllib.error.URLError as e:
            logger.warning(f"Network error downloading code for {function_name}: {e}")
            return None
        except ClientError as e:
            logger.warning(f"AWS error getting function code for {function_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving code for {function_name}: {e}")
            return None
    
    def analyze_code_with_bedrock(self, function_name: str, code_files: Dict[str, str], 
                                   current_runtime: str, target_runtime: str) -> Dict:
        """Use Bedrock to analyze code for compatibility issues"""
        if not self.bedrock_client or not code_files:
            return {"error": "No code available or Bedrock not initialized"}
        
        # Sanitize code content for logging (remove potential sensitive data)
        sanitized_files = {}
        for filename, content in code_files.items():
            # Basic sanitization - remove potential secrets
            sanitized_content = re.sub(r'(password|secret|key|token)\s*[:=]\s*["\'][^"\']+["\']', 
                                     r'\1: "[REDACTED]"', content, flags=re.IGNORECASE)
            sanitized_files[filename] = sanitized_content
        
        code_context = "\n\n".join([
            f"File: {filename}\n```{self.runtime_type}\n{content}\n```"
            for filename, content in sanitized_files.items()
        ])
        
        if self.runtime_type == 'nodejs':
            runtime_specific_guidance = NODEJS_ANALYSIS_GUIDANCE
        else:  # python
            runtime_specific_guidance = PYTHON_ANALYSIS_GUIDANCE
        
        prompt = BEDROCK_ANALYSIS_PROMPT_TEMPLATE.format(
            runtime_type=self.runtime_type.upper(),
            function_name=function_name,
            current_runtime=current_runtime,
            target_runtime=target_runtime,
            code_context=code_context,
            runtime_specific_guidance=runtime_specific_guidance
        )

        try:
            response = self.bedrock_client.invoke_model(
                modelId=self.bedrock_model,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1
                })
            )
            
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {"error": "Could not parse AI response", "raw_response": analysis_text}
            
            return analysis
            
        except ClientError as e:
            logger.error(f"Bedrock client error for {function_name}: {e}")
            return {"error": f"Bedrock client error: {str(e)}"}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {function_name}: {e}")
            return {"error": f"JSON decode error: {str(e)}"}
        except Exception as e:
            logger.error(f"Bedrock analysis failed for {function_name}: {e}")
            return {"error": f"Bedrock analysis failed: {str(e)}"}
    
    def update_function_runtime(self, lambda_client, function_name: str) -> Tuple[bool, str]:
        """Update a single function's runtime with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = lambda_client.update_function_configuration(
                    FunctionName=function_name,
                    Runtime=self.target_runtime
                )
                logger.info(f"Successfully updated {function_name} to {self.target_runtime}")
                return True, "Success"
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceConflictException' and attempt < max_retries - 1:
                    logger.warning(f"Resource conflict for {function_name}, retrying in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    logger.error(f"Failed to update {function_name}: {e}")
                    return False, str(e)
            except Exception as e:
                logger.error(f"Unexpected error updating {function_name}: {e}")
                return False, str(e)
        
        return False, "Max retries exceeded"
    
    async def process_function_async(self, lambda_client, function: Dict, region: str, 
                                    index: int, total: int) -> FunctionInfo:
        """Process a single function asynchronously"""
        func_info = FunctionInfo(
            name=function['FunctionName'],
            arn=function['FunctionArn'],
            region=region,
            runtime=function['Runtime']
        )
        
        logger.info(f"[{index}/{total}] Processing {func_info.name}")
        logger.info(f"    ARN: {func_info.arn}")
        logger.info(f"    Current Runtime: {func_info.runtime}")
        
        # AI Review if enabled
        if self.ai_review:
            logger.info(f"    🤖 Running AI code review...")
            
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                func_info.code_files = await loop.run_in_executor(
                    executor, 
                    self.get_function_code, 
                    lambda_client, 
                    func_info.name
                )
            
            if func_info.code_files:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    func_info.ai_analysis = await loop.run_in_executor(
                        executor,
                        self.analyze_code_with_bedrock,
                        func_info.name,
                        func_info.code_files,
                        func_info.runtime,
                        self.target_runtime
                    )
                
                if 'error' not in func_info.ai_analysis:
                    assessment_str = func_info.ai_analysis.get('overall_assessment', 'NOT_ANALYZED')
                    try:
                        func_info.assessment = AIAssessment(assessment_str)
                    except ValueError:
                        logger.warning(f"Invalid assessment value: {assessment_str}")
                        func_info.assessment = AIAssessment.ERROR
                    
                    logger.info(f"    Assessment: {func_info.assessment.value}")
                    
                    if func_info.assessment == AIAssessment.NEEDS_CHANGES:
                        logger.warning(f"    ⚠ Critical issues found - review required")
                    elif func_info.assessment == AIAssessment.REQUIRES_TESTING:
                        logger.warning(f"    ⚠ Testing recommended before upgrade")
                else:
                    func_info.assessment = AIAssessment.ERROR
                    logger.error(f"    ⚠ AI analysis error: {func_info.ai_analysis.get('error', 'Unknown')}")
            else:
                logger.warning(f"    ⚠ Could not retrieve code for analysis")
                func_info.assessment = AIAssessment.NOT_ANALYZED
        
        return func_info
    
    def get_mode_behavior(self) -> Dict[str, str]:
        """Get mode behavior description based on AI review status"""
        if self.ai_review:
            return MODE_BEHAVIOR_WITH_AI
        else:
            return MODE_BEHAVIOR_WITHOUT_AI
    
    def prompt_user_interactive(self, func_info: FunctionInfo) -> str:
        """Prompt user in interactive mode with AI-aware recommendations"""
        if self.ai_review and func_info.ai_analysis:
            print(f"\n    {'='*60}")
            print(f"    AI RECOMMENDATION")
            print(f"    {'='*60}")
            print(f"    Assessment: {func_info.assessment.value}")
            
            if func_info.ai_analysis.get('summary'):
                print(f"    Summary: {func_info.ai_analysis['summary']}")
            
            critical_count = len(func_info.ai_analysis.get('critical_issues', []))
            warning_count = len(func_info.ai_analysis.get('warnings', []))
            
            if critical_count > 0:
                print(f"    ⚠ Critical Issues: {critical_count}")
            if warning_count > 0:
                print(f"    ⚠ Warnings: {warning_count}")
            
            if func_info.assessment == AIAssessment.SAFE_TO_UPGRADE:
                print(f"    ✓ RECOMMENDATION: Safe to upgrade")
            elif func_info.assessment == AIAssessment.NEEDS_CHANGES:
                print(f"    ✗ RECOMMENDATION: Do NOT upgrade - code changes required")
            elif func_info.assessment == AIAssessment.REQUIRES_TESTING:
                print(f"    ⚠ RECOMMENDATION: Upgrade with caution - testing required")
            
            print(f"    {'='*60}")
        
        while True:
            if self.ai_review:
                response = input(f"\n    Update {func_info.name}? [y/n/q/d(etails)]: ").lower().strip()
            else:
                response = input(f"\n    Update {func_info.name}? [y/n/q]: ").lower().strip()
            
            if response in ['y', 'yes']:
                return 'yes'
            elif response in ['n', 'no']:
                return 'no'
            elif response in ['q', 'quit']:
                return 'quit'
            elif response in ['d', 'details'] and self.ai_review and func_info.ai_analysis:
                self.print_detailed_analysis(func_info.ai_analysis)
            else:
                if self.ai_review:
                    print("    Please enter 'y' (yes), 'n' (no), 'q' (quit), or 'd' (details)")
                else:
                    print("    Please enter 'y' (yes), 'n' (no), or 'q' (quit)")
    
    def should_update_in_force_mode(self, func_info: FunctionInfo) -> Tuple[Optional[bool], str]:
        """Determine if function should be updated in force mode with AI review"""
        if not self.ai_review:
            return True, "Force mode without AI review"
        
        if func_info.assessment == AIAssessment.SAFE_TO_UPGRADE:
            return True, "AI assessment: Safe to upgrade"
        elif func_info.assessment == AIAssessment.NEEDS_CHANGES:
            return False, "AI assessment: Critical issues - skipping"
        elif func_info.assessment == AIAssessment.REQUIRES_TESTING:
            return None, "AI assessment: Requires testing - prompting user"
        else:
            return False, f"AI assessment: {func_info.assessment.value} - skipping"
    
    def print_detailed_analysis(self, analysis: Dict):
        """Print detailed AI analysis"""
        print("\n    " + "="*60)
        print("    DETAILED AI ANALYSIS")
        print("    " + "="*60)
        
        if analysis.get('critical_issues'):
            print("\n    CRITICAL ISSUES:")
            for issue in analysis['critical_issues']:
                print(f"      • {issue.get('issue', 'N/A')}")
                print(f"        Location: {issue.get('location', 'N/A')}")
                print(f"        Fix: {issue.get('fix', 'N/A')}")
        
        if analysis.get('warnings'):
            print("\n    WARNINGS:")
            for warning in analysis['warnings']:
                print(f"      • {warning.get('issue', 'N/A')}")
                print(f"        Location: {warning.get('location', 'N/A')}")
        
        if analysis.get('recommendations'):
            print("\n    RECOMMENDATIONS:")
            for rec in analysis['recommendations']:
                print(f"      • {rec}")
        
        if analysis.get('dependencies_to_check'):
            print("\n    DEPENDENCIES TO CHECK:")
            for dep in analysis['dependencies_to_check']:
                print(f"      • {dep}")
        
        print("    " + "="*60 + "\n")
    
    def generate_report(self, all_functions: List[FunctionInfo], output_file: str = "lambda_upgrade_report.json"):
        """Generate comprehensive report"""
        report = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "runtime_type": self.runtime_type,
            "source_runtimes": self.source_runtimes,
            "target_runtime": self.target_runtime,
            "regions": self.regions,
            "mode": self.mode,
            "ai_review_enabled": self.ai_review,
            "total_functions": len(all_functions),
            "functions": []
        }
        
        for func_info in all_functions:
            func_report = {
                "function_name": func_info.name,
                "function_arn": func_info.arn,
                "region": func_info.region,
                "current_runtime": func_info.runtime,
                "updated": func_info.updated,
                "skipped": func_info.skipped,
                "failed": func_info.failed
            }
            
            if func_info.ai_analysis:
                func_report["ai_analysis"] = func_info.ai_analysis
                func_report["assessment"] = func_info.assessment.value
            
            if func_info.error_message:
                func_report["error_message"] = func_info.error_message
            
            report["functions"].append(func_report)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate summary
        summary_file = output_file.replace('.json', '_summary.txt')
        with open(summary_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("LAMBDA RUNTIME UPGRADE REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Generated: {report['generated_at']}\n")
            f.write(f"Runtime Type: {self.runtime_type.upper()}\n")
            f.write(f"Source Runtimes: {', '.join(self.source_runtimes)}\n")
            f.write(f"Target Runtime: {self.target_runtime}\n")
            f.write(f"Mode: {self.mode}\n")
            f.write(f"AI Review: {'Enabled' if self.ai_review else 'Disabled'}\n")
            f.write(f"Regions: {', '.join(self.regions)}\n")
            f.write(f"Total Functions: {len(all_functions)}\n\n")
            
            updated = sum(1 for f in all_functions if f.updated)
            skipped = sum(1 for f in all_functions if f.skipped)
            failed = sum(1 for f in all_functions if f.failed)
            
            f.write("EXECUTION SUMMARY:\n")
            f.write(f"  Updated: {updated}\n")
            f.write(f"  Skipped: {skipped}\n")
            f.write(f"  Failed: {failed}\n\n")
            
            if self.ai_review:
                safe = sum(1 for f in all_functions if f.assessment == AIAssessment.SAFE_TO_UPGRADE)
                needs_changes = sum(1 for f in all_functions if f.assessment == AIAssessment.NEEDS_CHANGES)
                requires_testing = sum(1 for f in all_functions if f.assessment == AIAssessment.REQUIRES_TESTING)
                
                f.write("AI ASSESSMENT SUMMARY:\n")
                f.write(f"  Safe to Upgrade: {safe}\n")
                f.write(f"  Needs Changes: {needs_changes}\n")
                f.write(f"  Requires Testing: {requires_testing}\n\n")
            
            f.write("="*70 + "\n")
            f.write("DETAILED FINDINGS\n")
            f.write("="*70 + "\n\n")
            
            for func_info in all_functions:
                f.write(f"\nFunction: {func_info.name}\n")
                f.write(f"Region: {func_info.region}\n")
                f.write(f"Current Runtime: {func_info.runtime}\n")
                f.write(f"Status: {'Updated' if func_info.updated else 'Skipped' if func_info.skipped else 'Failed' if func_info.failed else 'Not Processed'}\n")
                
                if func_info.ai_analysis and 'error' not in func_info.ai_analysis:
                    f.write(f"Assessment: {func_info.assessment.value}\n")
                    f.write(f"Summary: {func_info.ai_analysis.get('summary', 'N/A')}\n")
                    
                    if func_info.ai_analysis.get('critical_issues'):
                        f.write(f"\nCritical Issues ({len(func_info.ai_analysis['critical_issues'])}):\n")
                        for issue in func_info.ai_analysis['critical_issues']:
                            f.write(f"  • {issue.get('issue', 'N/A')}\n")
                            f.write(f"    Location: {issue.get('location', 'N/A')}\n")
                            f.write(f"    Fix: {issue.get('fix', 'N/A')}\n")
                
                f.write("\n" + "-"*70 + "\n")
        
        return output_file, summary_file
    
    async def process_region_async(self, region: str) -> Tuple[str, List[FunctionInfo]]:
        """Process all functions in a region asynchronously"""
        logger.info(f"\n{'='*70}")
        logger.info(f"Processing region: {region}")
        logger.info(f"{'='*70}")
        
        try:
            lambda_client = boto3.client('lambda', region_name=region)
            functions = self.list_deprecated_functions(lambda_client)
            
            if not functions:
                logger.info(f"✓ No functions found using {', '.join(self.source_runtimes)} in {region}")
                return region, []
            
            region_total = len(functions)
            logger.info(f"Found {region_total} function(s) using deprecated runtimes\n")
            
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def process_with_semaphore(func, idx):
                async with semaphore:
                    return await self.process_function_async(lambda_client, func, region, idx, region_total)
            
            tasks = [process_with_semaphore(func, i+1) for i, func in enumerate(functions)]
            function_infos = await asyncio.gather(*tasks)
            
            return region, function_infos
            
        except Exception as e:
            logger.error(f"✗ Error processing region {region}: {e}")
            return region, []
    
    async def run_async(self) -> None:
        """Main async execution method"""
        logger.info("=" * 70)
        logger.info("Lambda Runtime Update Tool with AI Review & Parallel Processing")
        logger.info("=" * 70)
        logger.info(f"Runtime Type: {self.runtime_type.upper()}")
        logger.info(f"Source Runtimes: {', '.join(self.source_runtimes)}")
        logger.info(f"Target Runtime: {self.target_runtime}")
        logger.info(f"Mode: {self.mode}")
        logger.info(f"AI Review: {'Enabled' if self.ai_review else 'Disabled'}")
        if self.ai_review:
            logger.info(f"Bedrock Model: {self.bedrock_model}")
        logger.info(f"Regions: {', '.join(self.regions)}")
        logger.info(f"Max Parallel Workers: {self.max_workers}")
        logger.info("\nMode Behavior:")
        for mode, behavior in self.get_mode_behavior().items():
            marker = "→" if mode == self.mode else " "
            logger.info(f"  {marker} {mode}: {behavior}")
        logger.info("=" * 70)
        
        # Phase 1: Analyze all functions in parallel
        logger.info(f"\n{'='*70}")
        logger.info("PHASE 1: DISCOVERY & ANALYSIS")
        logger.info("="*70)
        
        region_tasks = [self.process_region_async(region) for region in self.regions]
        region_results = await asyncio.gather(*region_tasks)
        
        all_functions = []
        for region, func_infos in region_results:
            all_functions.extend(func_infos)
        
        if not all_functions:
            logger.info(f"\n✓ No functions found using {', '.join(self.source_runtimes)} in any region")
            return
        
        logger.info(f"\n{'='*70}")
        logger.info(f"ANALYSIS COMPLETE: Found {len(all_functions)} function(s) total")
        logger.info(f"{'='*70}")
        
        # Phase 2: Update functions based on mode
        if self.mode == 'dry-run':
            logger.info("\n✓ Dry-run complete. No functions were updated.")
        else:
            logger.info(f"\n{'='*70}")
            logger.info("PHASE 2: RUNTIME UPDATES")
            logger.info("="*70 + "\n")
            
            quit_requested = False
            
            for func_info in all_functions:
                if quit_requested:
                    break
                
                logger.info(f"\nProcessing: {func_info.name} ({func_info.region})")
                
                if self.mode == 'interactive':
                    user_choice = self.prompt_user_interactive(func_info)
                    if user_choice == 'quit':
                        logger.warning("\n⚠ User requested quit. Stopping execution.")
                        quit_requested = True
                        break
                    elif user_choice == 'no':
                        logger.info(f"    ⊘ Skipped by user")
                        func_info.skipped = True
                        continue
                
                elif self.mode == 'force' and self.ai_review:
                    should_update, reason = self.should_update_in_force_mode(func_info)
                    
                    if should_update is None:
                        logger.info(f"    ⚠ {reason}")
                        user_choice = self.prompt_user_interactive(func_info)
                        if user_choice == 'quit':
                            logger.warning("\n⚠ User requested quit. Stopping execution.")
                            quit_requested = True
                            break
                        elif user_choice == 'no':
                            logger.info(f"    ⊘ Skipped by user")
                            func_info.skipped = True
                            continue
                    elif not should_update:
                        logger.info(f"    ⊘ {reason}")
                        func_info.skipped = True
                        continue
                    else:
                        logger.info(f"    ✓ {reason}")
                
                logger.info(f"    ⟳ Updating to {self.target_runtime}...")
                lambda_client = boto3.client('lambda', region_name=func_info.region)
                success, result = self.update_function_runtime(lambda_client, func_info.name)
                
                if success:
                    logger.info(f"    ✓ Successfully updated")
                    func_info.updated = True
                else:
                    logger.error(f"    ✗ Failed: {result}")
                    func_info.failed = True
                    func_info.error_message = result
                
                time.sleep(0.5)
        
        # Generate report
        if self.ai_review or self.mode != 'dry-run':
            logger.info(f"\n{'='*70}")
            logger.info("Generating Report...")
            report_file, summary_file = self.generate_report(all_functions)
            logger.info(f"✓ Report saved to: {report_file}")
            logger.info(f"✓ Summary saved to: {summary_file}")
        
        # Final summary
        logger.info(f"\n{'='*70}")
        logger.info("FINAL SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Mode: {self.mode}")
        logger.info(f"Total functions found: {len(all_functions)}")
        
        if self.mode == 'dry-run':
            logger.info(f"Functions analyzed: {len(all_functions)}")
        else:
            updated = sum(1 for f in all_functions if f.updated)
            skipped = sum(1 for f in all_functions if f.skipped)
            failed = sum(1 for f in all_functions if f.failed)
            
            logger.info(f"Successfully updated: {updated}")
            logger.info(f"Skipped: {skipped}")
            logger.info(f"Failed: {failed}")
        
        if self.ai_review:
            safe = sum(1 for f in all_functions if f.assessment == AIAssessment.SAFE_TO_UPGRADE)
            needs_changes = sum(1 for f in all_functions if f.assessment == AIAssessment.NEEDS_CHANGES)
            requires_testing = sum(1 for f in all_functions if f.assessment == AIAssessment.REQUIRES_TESTING)
            
            logger.info(f"\nAI Assessment Breakdown:")
            logger.info(f"  Safe to Upgrade: {safe}")
            logger.info(f"  Needs Changes: {needs_changes}")
            logger.info(f"  Requires Testing: {requires_testing}")
        
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
        description='Update Lambda functions with AI review and parallel processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=CLI_HELP_EXAMPLES
    )
    
    parser.add_argument('--regions', nargs='+', default=DEFAULT_REGIONS,
                       help=f'AWS regions to process (default: {DEFAULT_REGIONS})')
    parser.add_argument('--target-runtime', required=True,
                       help='Target runtime (e.g., nodejs22.x, python3.13)')
    parser.add_argument('--source-runtimes', nargs='+',
                       help='Source runtimes to upgrade from (auto-detected if not specified)')
    parser.add_argument('--mode', choices=['dry-run', 'interactive', 'force'],
                       default='interactive', help='Execution mode (default: interactive)')
    parser.add_argument('--ai-review', action='store_true',
                       help='Enable AI code analysis using AWS Bedrock')
    parser.add_argument('--bedrock-model', 
                       default='anthropic.claude-3-5-sonnet-20241022-v2:0',
                       help='Bedrock model for AI analysis')
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
            'target_runtime': args.target_runtime,
            'mode': args.mode,
            'source_runtimes': args.source_runtimes,
            'ai_review': args.ai_review,
            'bedrock_model': args.bedrock_model,
            'max_workers': args.max_workers
        }
        
        # Apply config file settings (command line args take precedence)
        for key, value in config.items():
            if key in updater_args and updater_args[key] is None:
                updater_args[key] = value
        
        updater = LambdaRuntimeUpdater(**updater_args)
        updater.run()
        
        logger.info("Lambda runtime update process completed successfully")
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
