#!/usr/bin/env python

# Usage:
#   python convert.py --files 'folder/*.docx' --format md

# Setup
#   pip install mammoth

import argparse
import glob
import mammoth
import os



def convert_word_file_to_html(inputfile, outputfile):
    with open(inputfile, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
    with open(outputfile, 'w') as html_file:
        html_file.write(result.value)


def convert_word_file_to_markdown(inputfile, outputfile):
    with open(inputfile, "rb") as docx_file:
        result = mammoth.convert_to_markdown(docx_file)
    with open(outputfile, 'w') as markdown_file:
        markdown_file.write(result.value)


def convert_word_files(format='html'):
    for file in files:
        basename = os.path.basename(file)
        basename, ext = os.path.splitext(basename)

        if format == 'html':
            print(f"Converting {basename}.{ext} to html/{basename}.html")
            if not os.path.isdir('html'):
                os.mkdir('html')

            convert_word_file_to_html(
                inputfile=file,
                outputfile=f'html/{basename}.html',
            )
        elif format == 'md':
            print(f"Converting {basename}.{ext} to md/{basename}.md")
            if not os.path.isdir('md'):
                os.mkdir('md')
            convert_word_file_to_markdown(
                inputfile=file,
                outputfile=f'md/{basename}.md',
            )



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', default='./*.docx')
    parser.add_argument('--format', choices=['md', 'html'], default='md')
    args = parser.parse_args()

    print(f"Format to convert to: {args.format}")
    print(f"Files to convert: {args.files}")
    files = glob.glob(args.files)
    print(f"Files found: {','.join(files)}")
    exit(0)

    if args.format == 'html':
        convert_word_files(format='html')
    elif args.format == 'md':
        convert_word_files(format='md')
