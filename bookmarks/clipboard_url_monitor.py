#!/usr/bin/env python3
"""
Clipboard URL Monitor

Monitors the clipboard for URLs and saves them to a CSV file with timestamps.

Setup:
    1. Install required dependencies:
       pip install pyperclip

    2. On macOS, ensure you have accessibility permissions if needed

Usage:
    # Run with default output file (urls.csv)
    ./clipboard_url_monitor.py

    # Specify custom output file
    ./clipboard_url_monitor.py --output my_urls.csv

    # Run in verbose mode
    ./clipboard_url_monitor.py --verbose

    Press Ctrl+C to stop monitoring.

Arguments:
    --output, -o        Output CSV file name (default: urls.csv)
    --verbose, -v       Enable verbose output
    --interval, -i      Check interval in seconds (default: 1.0)
"""

import pyperclip
import csv
import re
import argparse
import sys
import time
from datetime import datetime
from pathlib import Path


class ClipboardURLMonitor:
    """Monitor clipboard for URLs and save them to CSV."""

    # Comprehensive URL regex pattern
    URL_PATTERN = re.compile(
        r'http[s]?://'  # http:// or https://
        r'(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )

    def __init__(self, output_file='urls.csv', verbose=False, interval=1.0):
        """
        Initialize the clipboard monitor.

        Args:
            output_file: Path to the CSV output file
            verbose: Enable verbose output
            interval: Check interval in seconds
        """
        self.output_file = Path(output_file)
        self.verbose = verbose
        self.interval = interval
        self.last_clipboard = ""
        self.seen_urls = set()
        self.url_count = 0

        # Create CSV file with headers if it doesn't exist
        self._initialize_csv()

    def _initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.output_file.exists():
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'url'])
            if self.verbose:
                print(f"Created new CSV file: {self.output_file}")
        else:
            # Load existing URLs to avoid duplicates
            self._load_existing_urls()
            if self.verbose:
                print(f"Using existing CSV file: {self.output_file}")
                print(f"Loaded {len(self.seen_urls)} existing URLs")

    def _load_existing_urls(self):
        """Load existing URLs from CSV to avoid duplicates."""
        try:
            with open(self.output_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.seen_urls.add(row['url'])
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not load existing URLs: {e}")

    def _extract_urls(self, text):
        """
        Extract URLs from text.

        Args:
            text: Text to search for URLs

        Returns:
            List of unique URLs found
        """
        if not text:
            return []

        urls = self.URL_PATTERN.findall(text)
        return list(set(urls))  # Remove duplicates

    def _save_url(self, url):
        """
        Save a URL to the CSV file.

        Args:
            url: URL to save
        """
        timestamp = datetime.now().isoformat()

        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, url])

        self.seen_urls.add(url)
        self.url_count += 1
        print(f"✓ Saved URL [{self.url_count}]: {url}")

    def monitor(self):
        """Start monitoring the clipboard."""
        print(f"🔍 Monitoring clipboard for URLs...")
        print(f"📝 Saving to: {self.output_file.absolute()}")
        print(f"⏱️  Check interval: {self.interval}s")
        print(f"Press Ctrl+C to stop\n")

        try:
            while True:
                try:
                    # Get current clipboard content
                    current_clipboard = pyperclip.paste()

                    # Only process if clipboard has changed
                    if current_clipboard != self.last_clipboard:
                        self.last_clipboard = current_clipboard

                        # Extract URLs
                        urls = self._extract_urls(current_clipboard)

                        if urls:
                            if self.verbose:
                                print(f"Found {len(urls)} URL(s) in clipboard")

                            # Save new URLs
                            for url in urls:
                                if url not in self.seen_urls:
                                    self._save_url(url)
                                elif self.verbose:
                                    print(f"⊘ Skipped duplicate: {url}")

                except Exception as e:
                    if self.verbose:
                        print(f"Error checking clipboard: {e}")

                time.sleep(self.interval)

        except KeyboardInterrupt:
            print(f"\n\n✓ Monitoring stopped")
            print(f"📊 Total URLs saved: {self.url_count}")
            print(f"💾 Output file: {self.output_file.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description='Monitor clipboard for URLs and save to CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --output my_urls.csv
  %(prog)s --output urls.csv --verbose --interval 0.5
        """
    )

    parser.add_argument(
        '--output',
        '-o',
        default='urls.csv',
        help='Output CSV file name (default: urls.csv)'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--interval',
        '-i',
        type=float,
        default=1.0,
        help='Check interval in seconds (default: 1.0)'
    )

    args = parser.parse_args()

    # Validate interval
    if args.interval <= 0:
        print("Error: Interval must be greater than 0", file=sys.stderr)
        sys.exit(1)

    # Create and start monitor
    monitor = ClipboardURLMonitor(
        output_file=args.output,
        verbose=args.verbose,
        interval=args.interval
    )

    monitor.monitor()


if __name__ == '__main__':
    main()
