#!/usr/bin/env python

"""
Extract level 3 (###) headings from a markdown file into separate files.

This script parses a markdown file and extracts each level 3 heading and its content
into individual files. It's useful for splitting daily notes, customer engagements,
or project entries into separate files.

The script:
- Removes level 1 and 2 headers from the content
- Extracts each level 3 (###) heading and its content
- Creates sanitized filenames based on heading text
- Handles headings with yyyy.mm.dd date format
- Writes each section to a separate markdown file

Usage:
    ./extract_entries.py input.md [-o output_dir]

Arguments:
    input_file: Input markdown file to parse
    -o/--output-dir: Output directory for extracted files (default: entries)
"""

# Examples
# ./extract_entries.py weekly2021.md -o "entries/2021"
# ./extract_entries.py weekly2022.md -o "entries/2022"
# ./extract_entries.py weekly2023.md -o "entries/2023"
# ./extract_entries.py weekly2024.md -o "entries/2024"
# ./extract_entries.py weekly2025-H1.md -o "entries/2025-H1"
# ./extract_entries.py weekly2025-H2.md -o "entries/2025-H2"

import argparse
import os
import re
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('extract_entries.log'),
        logging.StreamHandler()
    ]
)

def remove_level1_headers(content):
    """
    Remove level 1 markdown headers (#) from the content.
    This removes lines that start with # (including the newline).
    """
    # Pattern to match entire lines starting with # (but not ## or ###)
    pattern = r'^# .*$\n?'
    cleaned_content = re.sub(pattern, '', content, flags=re.MULTILINE)
    return cleaned_content

def remove_level2_headers(content):
    """
    Remove level 2 markdown headers (##) from the content.
    This removes lines that start with ## (including the newline).
    """
    # Pattern to match entire lines starting with ##
    pattern = r'^## .*$\n?'
    cleaned_content = re.sub(pattern, '', content, flags=re.MULTILINE)
    return cleaned_content

def sanitize_filename(filename, max_length=100):
    """Remove non-standard characters and limit filename length."""
    # Remove or replace invalid filename characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Trim and limit length
    filename = filename.strip()[:max_length]
    return filename

def limit_trailing_newlines(text, max_newlines=2):
    """
    Limit the number of trailing newlines in text to max_newlines.
    """
    # Remove all trailing whitespace
    text = text.rstrip()
    # Add back the desired number of newlines
    return text + '\n' * max_newlines

def parse_markdown_file(input_file, output_dir):
    """
    Parse markdown file and extract ### headings into separate files.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove level 1 & 2 headers before processing
    content = remove_level1_headers(content)
    content = remove_level2_headers(content)
    logger.info(content)
    
    # Split content by any heading (to find boundaries)
    # Pattern to match ### headings specifically
    heading_pattern = r'^### (.+)$'
    
    # Find all ### headings and their positions
    matches = list(re.finditer(heading_pattern, content, re.MULTILINE))
    
    if not matches:
        logger.info("No ### headings found in the file.")
        print("No ### headings found in the file.")
        return
    
    for i, match in enumerate(matches):
        heading_text = match.group(1).strip()
        start_pos = match.end()
        
        # Find the end position (next heading of any level or end of file)
        if i < len(matches) - 1:
            # Find next heading (any level)
            next_heading = re.search(r'^#{1,6} ', content[start_pos:], re.MULTILINE)
            if next_heading:
                end_pos = start_pos + next_heading.start()
            else:
                end_pos = len(content)
        else:
            end_pos = len(content)
        
        # Extract body content
        body = content[start_pos:end_pos].strip()
        
        # Check if heading matches yyyy.mm.dd format
        date_pattern = r'^(\d{4}\.\d{2}\.\d{2})\s+(.+)$'
        date_match = re.match(date_pattern, heading_text)
        
        if date_match:
            # Standard format with date
            date = date_match.group(1)
            title = date_match.group(2).strip()
            filename = f"{date} {title}"
        else:
            # Non-standard format without date
            filename = heading_text
        
        # Sanitize filename
        filename = sanitize_filename(filename)
        filename += '.md'
        
        # Create the file content (including the heading)
        file_content = f"### {heading_text}\n\n{body}"
        
        # Limit trailing newlines to 2
        file_content = limit_trailing_newlines(file_content, max_newlines=2)
        
        # Write to file
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        logger.info(f"Created: {filename}")
    
    success_msg = f"Successfully extracted {len(matches)} entries to '{output_dir}/'"
    logger.info(success_msg)

def main():
    parser = argparse.ArgumentParser(
        description='Extract level 3 (###) headings from a markdown file into separate files. '
                    'Useful for splitting daily notes, customer engagements, or project entries.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s notes.md
  %(prog)s notes.md -o my_entries
  %(prog)s notes.md --output-dir project_logs
        '''
    )
    
    parser.add_argument('input_file', help='Input markdown file to parse')
    parser.add_argument('-o', '--output-dir', default='entries', help='Output directory for extracted entries (default: entries)')
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.isfile(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return 1
    
    print(f"Parsing '{args.input_file}'...")
    print(f"Output directory: '{args.output_dir}/'")
    print()
    
    parse_markdown_file(args.input_file, args.output_dir)

    # Move extract_entries.log file to the output directory
    if os.path.exists('extract_entries.log'):
        os.rename('extract_entries.log', os.path.join(args.output_dir, 'extract_entries.log'))
    return 0

if __name__ == "__main__":
    exit(main())
