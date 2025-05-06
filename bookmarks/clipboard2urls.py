#!/usr/bin/env python3

"""
URL Extractor - Extract URLs from macOS clipboard rich text
This code was ~80% generated using Perplexity AI chat and generative AI coding assistants
"""

import argparse
import binascii
import re
import subprocess
import sys



def get_clipboard_rtf():
    """
    Get content from macOS clipboard, based on the following example from Perplexity AI:
    $ osascript -e 'try' -e 'get the clipboard as «class RTF »' -e 'end try' | perl -ne 'print pack "H*", $1 if /«data RTF (.*?)»/'
    """
    try:
        # Run AppleScript to get raw RTF hex data
        result = subprocess.run(
            ['osascript', '-e', 'try', '-e', 'get the clipboard as «class RTF »', '-e', 'end try'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract hex string using regex
        match = re.search(r'«data RTF (.*?)»', result.stdout)
        if not match:
            return None
            
        # Convert hex to bytes and decode to string
        hex_data = match.group(1)
        rtf_bytes = binascii.unhexlify(hex_data)
        return rtf_bytes.decode('latin-1')  # Preserve all byte values
        
    except (subprocess.CalledProcessError, binascii.Error):
        return None



def get_clipboard_pbpaste():
    """Retrieves content from clipboard using pbpaste"""

    content = ""
    
    # Try to get rich text (HTML) content first
    try:
        result = subprocess.run(['pbpaste', '-Prefer', 'rtf'], capture_output=True, text=True)
        content = result.stdout
    except subprocess.CalledProcessError:
        pass
        
    # If no URLs found in rich text, try HTML format
    if not content or not extract_urls(content):
        try:
            result = subprocess.run(['pbpaste', '-Prefer', 'html'], capture_output=True, text=True)
            content = result.stdout
        except subprocess.CalledProcessError:
            pass
    
    # If still no URLs, fall back to plain text
    if not content or not extract_urls(content):
        try:
            result = subprocess.run(['pbpaste'], capture_output=True, text=True, check=True)
            content = result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error accessing clipboard: {e}", file=sys.stderr)
            return ""
            
    return content



def extract_urls(text):
    """
    Extract URLs from text

    Regex matches URLs starting with http:// or https://,
    followed by a domain (word chars, hyphens, dots),
    then any non-whitespace chars.
    """

    # Breakdown:
    # https?     - matches 'http' with optional 's'
    # ://       - matches '://' literally
    # [\w\-\.]+ - matches 1+ word chars, hyphens or dots (domain)
    # [^\s]*    - matches 0+ non-whitespace chars (rest of URL)

    url_pattern = r'https?://[\w\-\.]+[^\s]*'
    
    # Find all URLs in the text
    urls = re.findall(url_pattern, text)
    return urls



def clean_rtf_text(rtf_title):
    """Cleans RTF control words from extracted title"""
    return re.sub(r'\\[a-zA-Z]+\d* ?|[{}]', '', rtf_title).strip()


def extract_urls_rich_text(rtf_text):
    """
    Extracts all (URL, title) pairs from rich text following the pattern below:
    """

    # \f1\fs18 \AppleTypeServices {\listtext	\uc0\u8226 	}{\field{\*\fldinst{HYPERLINK "https://example.com/hyperlink/example1.html"}}{\fldrslt 
    # \f0\fs26 \AppleTypeServices\AppleTypeServicesF2293774 HyperLink Title 1 Goes Here}}
    # \f0\fs26 \AppleTypeServices\AppleTypeServicesF2293774 \
    # \ls2\ilvl0
    # \f1\fs18 \AppleTypeServices {\listtext	\uc0\u8226 	}{\field{\*\fldinst{HYPERLINK "https://example.com/hyperlink/example2.html"}}{\fldrslt 
    # \f0\fs26 \AppleTypeServices\AppleTypeServicesF2293774 HyperLink Title 2 Goes Here}}
    # \f0\fs26 \AppleTypeServices\AppleTypeServicesF2293774 \
    # \ls2\ilvl0

    pattern = re.compile(r'HYPERLINK "([^"]+)"}}\{\\fldrslt\s*([^}]+)')
    matches = pattern.findall(rtf_text)
    
    def clean_title(rtf_title):
        """
        Removes RTF control symbols from title
        Removes (opens in a new tab) from title
        """
        text = re.sub(r'\\[a-zA-Z]+\d* ?|[{}]', '', rtf_title).strip()
        return re.sub(r'\s*\(opens in a new tab\)\s*', '', text)
    
    return [(url, clean_title(title)) for url, title in matches]



def set_clipboard_content(content):
    """Set content to macOS clipboard."""
    try:
        # Use pbcopy to set clipboard content
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(content.encode('utf-8'))
        return True
    except Exception as e:
        print(f"Error setting clipboard: {e}", file=sys.stderr)
        return False



def get_clipboard():
    """Get content from clipboard, trying different methods."""

    # Option 1: RTF
    rtf_content = get_clipboard_rtf()
    if rtf_content:
        print("RTF content retrieved successfully!")
        # rtf_content now contains the RTF-formatted string
        return rtf_content
    else:
        print("No RTF data found in clipboard", file=sys.stderr)

    # Option 2: pbpaste
    pbpaste_content = get_clipboard_pbpaste()
    if pbpaste_content:
        return pbpaste_content
    else:
        print("No pbpaste data found in clipboard", file=sys.stderr)



def links_to_markdown_string(links):
    """Converts list of (url, title) pairs to a single markdown string."""
    return '\n'.join(f'[{title}]({url})' for url, title in links)


def save_links_to_csv(links):
    """Converts list of (url, title) pairs to a comma-separated string."""
    return '\n'.join(f'{title},{url}' for url, title in links)


def save_url_pairs(pairs, filename='', clipboard=False):
    md_string = links_to_markdown_string(pairs)
    error_encountered = False
    if filename:
        try:
            with open(filename, 'w') as f:
                f.write(md_string)
            print(f"URLs written to {filename}")
        except IOError as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            error_encountered = True
    
    if clipboard:
        # csv_string = save_links_to_csv(pairs)
        if set_clipboard_content(md_string):
            print("URLs copied back to clipboard")
        else:
            error_encountered = True
    return error_encountered


def main(args):
    clipboard_text = get_clipboard()
    with open("clipboard.rtf.txt", 'w') as f:
        f.write(clipboard_text)

    url_title_pairs = extract_urls_rich_text(clipboard_text)
    return save_url_pairs(url_title_pairs, args.file, args.clipboard)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract URLs from macOS clipboard')
    parser.add_argument('-f', '--file', default='clipboard.md',
                        help='Output to file')
    parser.add_argument('-c', '--clipboard', default=True, 
                        help='Copy results back to clipboard')
    args = parser.parse_args()
    sys.exit(main(args))
