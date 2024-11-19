#!/usr/bin/env python

import json
import random
import argparse
from pathlib import Path

def read_jsonl(input_file):
    """Read JSONL file and return list of JSON objects"""
    data = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                data.append(json.loads(line.strip()))
    return data

def sample_data(data, sample_rate):
    """Sample data at specified rate"""
    if not 0 < sample_rate <= 100:
        raise ValueError("Sample rate must be between 0 and 100")
    
    sample_size = int(len(data) * (sample_rate / 100))
    return random.sample(data, sample_size)

def write_jsonl(data, output_file):
    """Write data to JSONL file"""
    with open(output_file, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

def main():
    parser = argparse.ArgumentParser(description='Sample a JSONL file at a specified rate')
    parser.add_argument('input_file', help='Input JSONL file path')
    parser.add_argument('sample_rate', type=float, help='Sampling rate (1-100)')
    parser.add_argument('output_file', help='Output JSONL file path')
    
    args = parser.parse_args()
    
    try:
        # Validate input file exists
        if not Path(args.input_file).is_file():
            raise FileNotFoundError(f"Input file not found: {args.input_file}")
        
        # Read data
        data = read_jsonl(args.input_file)
        
        if not data:
            raise ValueError("Input file is empty")
        
        # Sample data
        sampled_data = sample_data(data, args.sample_rate)
        
        # Write output
        write_jsonl(sampled_data, args.output_file)
        
        print(f"Successfully sampled {args.sample_rate}% of data")
        print(f"Input records: {len(data)}")
        print(f"Output records: {len(sampled_data)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()
