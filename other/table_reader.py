#!/usr/bin/env python
"""
Reads tables from spreadsheets and pdfs
Requirements: pandas, xlrd, tabula-py
"""

import argparse
import pandas as pd
import tabula


class PDF_Table():

    def __init__(self, filename):
        # assert filename.endswith('.pdf')
        self._df = tabula.read_pdf(filename)


class XL_Table():

    def __init__(self, filename):
        # assert (filename.endswith('.xlsx') or 
        #         filename.endswith('.xls'))
        self._xl = pd.ExcelFile(filename)
    
    def sheet_names(self):
        return self._xl.sheet_names

    def extract_sheet(self, sheet_name, **params):
        return self._xl.parse(sheet_name, **params)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='Name of file')
    args = parser.parse_args()

    xl = XL_Table(args.filename)
    sheets = xl.sheet_names()
    print(f"Sheet Names: {', '.join(sheets)}")
    print("First sheet:")
    df = xl.extract_sheet(sheets[0], header=0)
    print(df)
