#!/usr/bin/env python

import argparse
import tabula


def pdf2df(pdf_file):
    """
    Converts a single .pdf file into a dataframe
    """
    return tabula.read_pdf(pdf_file, pages='all')


def pdf2csv(pdf_file, csv_file):
    """
    Converts a single .pdf file into a .csv file
    """
    tabula.convert_into(pdf_file, csv_file, output_format="csv", pages='all', multiple_tables=True)
    print(f"Created: {csv_file}")


def pdf_folder2csv(pdf_folder):
    """
    Converts a folder of .pdf files into multiple .csv files
    """
    tabula.convert_into_by_batch(pdf_folder, output_format='csv', pages='all')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', default='', help='.pdf file to parse')
    parser.add_argument('--csv', default='', help='.csv output file')
    parser.add_argument('--folder', default='', help='.pdf folder to parse')
    args = parser.parse_args()

    if args.pdf != '':
        if args.csv == '':
            df = pdf2df(args.pdf)
            print(df)
        else:
            pdf2csv(args.pdf, args.csv)

    if args.folder != '':
        pdf_folder2csv(args.folder)
