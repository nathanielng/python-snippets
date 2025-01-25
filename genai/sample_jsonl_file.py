#!/usr/bin/env python

# Description:
#   Extracts a sample fraction (e.g. 10%) of a JSONL file

# Usage:
#   pip install anyascii
#   export AWS_DEFAULT_REGION="us-west-2"
#   python sample_jsonl_file.py --json answers.jsonl --fraction 0.10

import argparse
import json
import jsonlines
import os
import random

from anyascii import anyascii



def check_duplicates(data):
    """
    Returns true if duplicates exist
    """
    import pandas as pd
    df = pd.DataFrame(data)
    n_total = len(df)

    df.drop_duplicates(inplace=True)
    n_unique = len(df)

    print(f'Statistics: {n_total} total instruction tuning pairs out of which {n_unique} are unique')
    return n_unique < n_total


def load_json_file(json_file):
    _, ext = os.path.splitext(json_file)
    if ext == ".jsonl":
        data = []
        with jsonlines.open(json_file, mode='r') as reader:
            for row in reader.iter(type=dict, skip_invalid=True):
                data.append(row)
    elif ext == ".json":
        with open(json_file, 'r') as f:
            data = json.load(f)

    return data


def reformat_and_clean(data):
    new_data = []
    for d in data:
        new_data.append({
            "instruction": d["question"],
            "context": "",
            "response": anyascii(d["answer"])
        })
    return new_data


def create_jsonl_subsets(input_data, output_json, fraction):
    data1 = input_data

    # Step 2: Sample data
    n = len(data1)
    n_samples = int((fraction*100*n)//100)
    data2 = random.sample(data1, n_samples)

    # Step 3: Save data
    with jsonlines.open(output_json, mode='w') as f:
        f.write_all(data2)
        print(f"Saved {len(data2)} rows to {output_json}")



def main(args):
    input_json = args.json
    fraction = args.fraction

    # Load input json
    data0 = load_json_file(input_json)
    n = len(data0)

    # Generate output filename
    basename, _ = os.path.splitext(input_json)
    n_samples = int((fraction*100*n)//100)
    output_json = f"{basename}-{100*fraction:03.0f}-{n_samples}-of-{n}.jsonl"

    print(f"Loaded: {n} instruction tuning pairs")
    print(f"Rows to sample: {n_samples}")
    print(f"Output file: {output_json}")

    # Create subset of JSONL file
    create_jsonl_subsets(
        input_data = data0,
        output_json = output_json,
        fraction = fraction
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', type=str, required=True)
    parser.add_argument('--fraction', type=float, required=True)
    args = parser.parse_args()

    main(args)
