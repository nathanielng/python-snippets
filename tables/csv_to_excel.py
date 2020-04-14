#!/usr/bin/env python

# Converts a list of .csv files to
# worksheets in an Excel file

import argparse
import os
import pandas as pd


def process(files, excel_file):
    with pd.ExcelWriter(excel_file) as writer:
        for file in files:
            df = pd.read_csv(file)
            sheet_name, _ = os.path.splitext(os.path.basename(file))
            print(f"Writing sheet: '{sheet_name}' to {excel_file}")
            df.to_excel(writer, sheet_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts a list of .csv files to sheets in an Excel file')
    parser.add_argument('--files', help='Comma-separated file list')
    parser.add_argument('--excel', help='Excel output file')
    args = parser.parse_args()
    process(args.files.split(','), args.excel)

