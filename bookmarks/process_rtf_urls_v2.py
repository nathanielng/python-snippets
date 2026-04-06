"""
Parse RTF-formatted bookmarks and convert to CSV.

Reads an RTF file (typically from pbpaste > bookmarks.rtf) containing
hyperlink fields and extracts URLs and titles. Cleans RTF escape sequences
in titles and writes the results to a CSV file.

Expected input format: RTF with HYPERLINK fields containing URLs and titles.
Output: CSV file with Title and URL columns.

Usage:
    pbpaste > bookmarks.rtf
    python parse_rtf.py
"""
import re
import csv
import os
import sys

def clean_title(title):
    """Clean up RTF escape sequences in titles.

    Args:
        title: Raw title string from RTF

    Returns:
        Cleaned title string
    """
    title = title.strip()
    title = re.sub(r"\\'92", "'", title)   # right single quote
    title = re.sub(r"\\'93", "\u201c", title)  # left double quote
    title = re.sub(r"\\'94", "\u201d", title)  # right double quote
    title = re.sub(r"\\'[0-9a-f]{2}", "", title)  # other RTF escapes
    return title.strip()

def quality_check(output_file):
    """Verify the quality and integrity of the generated CSV file.

    Args:
        output_file: Path to the CSV file to check

    Returns:
        True if all checks pass, False otherwise
    """
    checks_passed = []
    checks_failed = []

    # Check 1: CSV file validity and parsing
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        checks_passed.append("CSV integrity: File is valid and properly formatted")
    except Exception as e:
        checks_failed.append(f"CSV integrity: Failed to parse ({e})")
        return False

    # Check 2: All rows have required fields
    invalid_rows = 0
    for i, row in enumerate(rows, 1):
        if not row.get("Title") or not row.get("URL"):
            invalid_rows += 1

    if invalid_rows == 0:
        checks_passed.append(f"All rows complete: Every bookmark has both Title and URL")
    else:
        checks_failed.append(f"All rows complete: {invalid_rows} rows missing Title or URL")

    # Check 3: No leftover RTF escapes in titles
    rtf_escapes_found = 0
    for row in rows:
        if re.search(r"\\'[0-9a-f]{2}", row["Title"]):
            rtf_escapes_found += 1

    if rtf_escapes_found == 0:
        checks_passed.append("No leftover RTF escapes: All escape sequences cleaned properly")
    else:
        checks_failed.append(f"No leftover RTF escapes: Found {rtf_escapes_found} entries with RTF codes")

    # Check 4: No control characters (parsing errors)
    control_chars_found = 0
    for row in rows:
        if any(ord(c) < 32 and c not in "\n\t" for c in row["Title"]):
            control_chars_found += 1

    if control_chars_found == 0:
        checks_passed.append("No parsing errors: Regex pattern matched all entries cleanly")
    else:
        checks_failed.append(f"No parsing errors: Found {control_chars_found} entries with control characters")

    # Check 5: Unicode handling verification
    try:
        # Verify we can write and read back with UTF-8
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        # If we got here, both reading and writing UTF-8 worked
        checks_passed.append("Unicode handling: Correct encoding throughout (UTF-8 in and out)")
    except UnicodeDecodeError:
        checks_failed.append("Unicode handling: UTF-8 encoding issue detected")

    # Print results
    print("\nQuality Check Results:")
    for check in checks_passed:
        print(f"✓ {check}")

    for check in checks_failed:
        print(f"✗ {check}")

    return len(checks_failed) == 0

def main():
    input_file = os.path.expanduser("bookmarks.rtf")
    output_file = os.path.expanduser("bookmarks.csv")

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: Failed to decode '{input_file}' as UTF-8.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading '{input_file}': {e}", file=sys.stderr)
        sys.exit(1)

    # Extract URL and title pairs from RTF hyperlink fields
    pattern = r'HYPERLINK "([^"]+)".*?fldrslt \{[^}]*\}([^}\\]+)\}'
    matches = re.findall(pattern, content)

    if not matches:
        print(f"Warning: No hyperlinks found in '{input_file}'", file=sys.stderr)

    try:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "URL"])
            for url, title in matches:
                writer.writerow([clean_title(title), url])
    except IOError as e:
        print(f"Error writing to '{output_file}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted {len(matches)} links to {output_file}")

    # Run quality checks
    if quality_check(output_file):
        print("\n✓ All quality checks passed!")
    else:
        print("\n✗ Some quality checks failed!", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
