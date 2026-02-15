#!/usr/bin/env python3
"""
Social Media Content Extractor

A robust tool for extracting metadata and content from social media URLs across multiple platforms.

Features:
    - Multi-platform support: LinkedIn, X (Twitter), Instagram, YouTube
    - CSV file processing: Read URLs from CSV, extract data, and update the file
    - Smart filtering: Process only empty rows by default, or filter by specific platforms
    - Flexible output: Extract titles, authors, content, and platform-specific metadata

Supported Platforms:
    - LinkedIn: Posts and articles (titles, authors, content from meta tags)
    - X/Twitter: Tweets and posts (titles, authors, tweet content)
    - Instagram: Posts and reels (captions, authors via meta tags)
    - YouTube: Videos and community posts (titles, descriptions, channel names)
    - AWS Blogs: AWS blog posts (titles, authors, content, publish dates, categories)
    - GitHub: Repositories, issues, PRs, GitHub Pages (titles, descriptions, authors)

CSV Processing:
    The tool can read a CSV file containing URLs and automatically populate missing data
    in the title, author, and content columns. By default, it only processes rows where
    all three fields are empty, preventing overwriting of existing data.

    After processing, completed rows are automatically moved to platform-specific CSV files:
    - LinkedIn posts → linkedin.csv
    - X/Twitter posts → x.csv
    - Instagram posts → instagram.csv
    - YouTube videos → youtube.csv

    New rows are always added to the top of these files, keeping the most recent content first.

Usage:
    # Process urls.csv (default - only empty rows, move to platform CSVs)
    python info_extractor.py

    # Process a single URL
    python info_extractor.py https://linkedin.com/posts/...

    # Process a different CSV file
    python info_extractor.py --csv my_urls.csv

    # Process only LinkedIn URLs (moves to linkedin.csv)
    python info_extractor.py --platform linkedin

    # Process only Instagram URLs (moves to instagram.csv)
    python info_extractor.py --platform instagram

    # Process all rows (including non-empty ones)
    python info_extractor.py --force

    # Keep completed rows in urls.csv instead of moving them
    python info_extractor.py --no-move

Environment Variables:
    YOUTUBE_API_KEY: Optional YouTube Data API key for enhanced video metadata
    TWITTER_BEARER_TOKEN: Optional X/Twitter API bearer token for full tweet access
                          (Required for X content - scraping is blocked by login walls)
    SAVE_RAW_HTML: Set to 'true' to include raw HTML in extraction results

Important Notes:
    - X/Twitter: Scraping is heavily restricted. For reliable extraction, set up
      TWITTER_BEARER_TOKEN with your X API credentials. Without it, only basic
      metadata (like author from URL) will be extracted.
    - Instagram: Limited by login requirements, best-effort extraction
    - YouTube: Works well without API key, but API provides richer metadata
    - LinkedIn: Generally works well with scraping

Requirements:
    - requests: HTTP client for fetching URLs
    - beautifulsoup4: HTML parsing
    - python-dotenv: Environment variable management
"""

import argparse
import csv
import logging
import os
import re
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SocialMediaExtractor:
    """Extracts content from various social media platforms."""
    
    def __init__(self):
        """Initialize the extractor with necessary headers and configuration."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # API keys from environment (if available)
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
    def get_platform(self, url: str) -> str:
        """
        Identify the platform from a URL.

        Args:
            url: The URL to check

        Returns:
            Platform name ('linkedin', 'x', 'instagram', 'youtube', 'aws', 'github', or 'unknown')
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')

        if 'linkedin.com' in domain:
            return 'linkedin'
        elif 'x.com' in domain or 'twitter.com' in domain:
            return 'x'
        elif 'instagram.com' in domain:
            return 'instagram'
        elif 'youtube.com' in domain or 'youtu.be' in domain:
            return 'youtube'
        elif 'aws.amazon.com' in domain and '/blogs/' in url:
            return 'aws'
        elif 'github.com' in domain or 'github.io' in domain:
            return 'github'
        else:
            return 'unknown'

    def extract(self, url: str) -> Dict[str, Any]:
        """
        Extract content from a social media URL.

        Args:
            url: The URL to extract content from

        Returns:
            Dictionary containing title, content, platform, and metadata
        """
        logger.info(f"Processing URL: {url}")

        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')

        try:
            if 'linkedin.com' in domain:
                return self._extract_linkedin(url)
            elif 'x.com' in domain or 'twitter.com' in domain:
                return self._extract_x(url)
            elif 'instagram.com' in domain:
                return self._extract_instagram(url)
            elif 'youtube.com' in domain or 'youtu.be' in domain:
                return self._extract_youtube(url)
            elif 'aws.amazon.com' in domain and '/blogs/' in url:
                return self._extract_aws(url)
            elif 'github.com' in domain or 'github.io' in domain:
                return self._extract_github(url)
            else:
                logger.warning(f"Unsupported platform: {domain}")
                return {
                    'platform': 'unknown',
                    'url': url,
                    'error': 'Unsupported platform'
                }
        except Exception as e:
            logger.error(f"Error extracting from {url}: {e}", exc_info=True)
            return {
                'platform': domain,
                'url': url,
                'error': str(e)
            }
    
    def _extract_linkedin(self, url: str) -> Dict[str, Any]:
        """Extract content from LinkedIn post."""
        logger.info("Extracting LinkedIn content")
        
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract from meta tags first (more reliable)
        title = None
        content = None
        author = None
        
        # OpenGraph tags
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        
        if og_title:
            title = og_title.get('content', '').strip()
        
        if og_description:
            content = og_description.get('content', '').strip()
        
        # Try to find author
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            author = author_meta.get('content', '').strip()
        
        # Fallback: Try to extract from page structure
        if not content:
            # LinkedIn often uses specific class names for post content
            post_content = soup.find('div', class_=re.compile(r'feed-shared-update-v2__description'))
            if post_content:
                content = post_content.get_text(strip=True, separator='\n')
        
        return {
            'platform': 'linkedin',
            'url': url,
            'title': title or 'LinkedIn Post',
            'content': content,
            'author': author,
            'raw_html': str(soup) if os.getenv('SAVE_RAW_HTML') == 'true' else None
        }
    
    def _extract_x(self, url: str) -> Dict[str, Any]:
        """Extract content from X (Twitter) post."""
        logger.info("Extracting X (Twitter) content")

        # Try API first if bearer token is available
        if self.twitter_bearer_token:
            try:
                return self._extract_x_api(url)
            except Exception as e:
                logger.warning(f"X API extraction failed, falling back to scraping: {e}")

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title = None
        content = None
        author = None

        # Try multiple meta tag strategies
        # 1. Twitter Card tags (preferred)
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        twitter_description = soup.find('meta', attrs={'name': 'twitter:description'})
        twitter_creator = soup.find('meta', attrs={'name': 'twitter:creator'})

        # 2. OpenGraph tags (fallback)
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')

        # 3. Standard meta tags
        meta_description = soup.find('meta', attrs={'name': 'description'})

        # Extract title
        if twitter_title:
            title = twitter_title.get('content', '').strip()
        elif og_title:
            title = og_title.get('content', '').strip()

        # Extract content/description
        if twitter_description:
            content = twitter_description.get('content', '').strip()
        elif og_description:
            content = og_description.get('content', '').strip()
        elif meta_description:
            content = meta_description.get('content', '').strip()

        # Extract author
        if twitter_creator:
            author = twitter_creator.get('content', '').strip().lstrip('@')
        elif title:
            # Try to extract from title patterns
            # Pattern 1: "Author on X: content"
            if ' on X:' in title:
                author = title.split(' on X:')[0].strip()
            # Pattern 2: "Author: content"
            elif ':' in title and len(title.split(':')[0]) < 50:
                potential_author = title.split(':')[0].strip()
                # Only use if it looks like a username (short, no special chars except _)
                if len(potential_author) < 30 and not any(c in potential_author for c in ['(', ')', '[', ']']):
                    author = potential_author

        # Try to extract from URL if we have a status URL
        if not author and '/status/' in url:
            # URL pattern: https://x.com/username/status/123456
            parts = url.split('/')
            try:
                username_idx = parts.index('x.com') + 1
                if username_idx < len(parts) and parts[username_idx + 1] == 'status':
                    author = parts[username_idx]
            except (ValueError, IndexError):
                pass

        # Use title as content if content is empty but title has substance
        if not content and title and len(title) > 30:
            # If title looks like it contains the tweet content, use it
            if ' on X:' in title:
                content = title.split(' on X:')[1].strip()
            elif author and title.startswith(author):
                # Remove author name from beginning if present
                content = title[len(author):].lstrip(':').strip()

        return {
            'platform': 'x',
            'url': url,
            'title': title or 'X Post',
            'content': content or 'Content unavailable (login required)',
            'author': author,
            'raw_html': str(soup) if os.getenv('SAVE_RAW_HTML') == 'true' else None
        }

    def _extract_x_api(self, url: str) -> Dict[str, Any]:
        """Extract content from X (Twitter) post using API."""
        logger.info("Using X API for tweet extraction")

        # Extract tweet ID from URL
        tweet_id = None
        if '/status/' in url:
            parts = url.split('/status/')
            if len(parts) > 1:
                tweet_id = parts[1].split('?')[0].split('/')[0]

        if not tweet_id:
            raise ValueError("Could not extract tweet ID from URL")

        # X API v2 endpoint
        api_url = f"https://api.twitter.com/2/tweets/{tweet_id}"
        params = {
            'tweet.fields': 'author_id,created_at,text,public_metrics',
            'expansions': 'author_id',
            'user.fields': 'username,name'
        }

        headers = {
            'Authorization': f'Bearer {self.twitter_bearer_token}'
        }

        response = self.session.get(api_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        if 'data' not in data:
            raise ValueError("Tweet not found")

        tweet = data['data']
        author_info = data.get('includes', {}).get('users', [{}])[0]

        return {
            'platform': 'x',
            'url': url,
            'tweet_id': tweet_id,
            'title': f"{author_info.get('name', 'User')} on X",
            'content': tweet.get('text', ''),
            'author': author_info.get('username', ''),
            'author_name': author_info.get('name', ''),
            'created_at': tweet.get('created_at', ''),
            'metrics': tweet.get('public_metrics', {}),
            'raw_html': None
        }

    def _extract_instagram(self, url: str) -> Dict[str, Any]:
        """Extract content from Instagram post."""
        logger.info("Extracting Instagram content")
        
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = None
        content = None
        author = None
        
        # OpenGraph tags
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        
        if og_title:
            title = og_title.get('content', '').strip()
        
        if og_description:
            content = og_description.get('content', '').strip()
        
        # Extract author from title (usually "Author on Instagram: content")
        if title and ' on Instagram:' in title:
            author = title.split(' on Instagram:')[0].strip()
        
        return {
            'platform': 'instagram',
            'url': url,
            'title': title or 'Instagram Post',
            'content': content,
            'author': author,
            'raw_html': str(soup) if os.getenv('SAVE_RAW_HTML') == 'true' else None
        }
    
    def _extract_youtube(self, url: str) -> Dict[str, Any]:
        """Extract content from YouTube post or video."""
        logger.info("Extracting YouTube content")
        
        # Determine if it's a community post or video
        is_community_post = '/post/' in url
        
        if is_community_post:
            return self._extract_youtube_post(url)
        else:
            return self._extract_youtube_video(url)
    
    def _extract_youtube_post(self, url: str) -> Dict[str, Any]:
        """Extract content from YouTube community post."""
        logger.info("Extracting YouTube community post")
        
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = None
        content = None
        author = None
        
        # OpenGraph tags
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        
        if og_title:
            title = og_title.get('content', '').strip()
        
        if og_description:
            content = og_description.get('content', '').strip()
        
        # Try to extract author from meta tags
        author_meta = soup.find('link', attrs={'itemprop': 'name'})
        if author_meta:
            author = author_meta.get('content', '').strip()
        
        return {
            'platform': 'youtube',
            'content_type': 'community_post',
            'url': url,
            'title': title or 'YouTube Community Post',
            'content': content,
            'author': author,
            'raw_html': str(soup) if os.getenv('SAVE_RAW_HTML') == 'true' else None
        }
    
    def _extract_youtube_video(self, url: str) -> Dict[str, Any]:
        """Extract content from YouTube video."""
        logger.info("Extracting YouTube video")
        
        # Extract video ID
        video_id = self._extract_youtube_video_id(url)
        
        if not video_id:
            raise ValueError("Could not extract YouTube video ID")
        
        # Try API first if available
        if self.youtube_api_key:
            return self._extract_youtube_video_api(video_id)
        
        # Fallback to scraping
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        response = self.session.get(watch_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = None
        description = None
        author = None
        
        # Meta tags
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        
        if og_title:
            title = og_title.get('content', '').strip()
        
        if og_description:
            description = og_description.get('content', '').strip()
        
        # Channel name
        author_meta = soup.find('link', attrs={'itemprop': 'name'})
        if author_meta:
            author = author_meta.get('content', '').strip()
        
        return {
            'platform': 'youtube',
            'content_type': 'video',
            'url': url,
            'video_id': video_id,
            'title': title or 'YouTube Video',
            'content': description,
            'author': author,
            'raw_html': str(soup) if os.getenv('SAVE_RAW_HTML') == 'true' else None
        }
    
    def _extract_youtube_video_api(self, video_id: str) -> Dict[str, Any]:
        """Extract YouTube video data using API."""
        logger.info(f"Using YouTube API for video {video_id}")
        
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': video_id,
            'key': self.youtube_api_key
        }
        
        response = self.session.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('items'):
            raise ValueError("Video not found")
        
        item = data['items'][0]
        snippet = item['snippet']
        
        return {
            'platform': 'youtube',
            'content_type': 'video',
            'video_id': video_id,
            'title': snippet['title'],
            'content': snippet['description'],
            'author': snippet['channelTitle'],
            'published_at': snippet['publishedAt'],
            'tags': snippet.get('tags', []),
            'category_id': snippet['categoryId'],
            'statistics': item.get('statistics', {}),
            'url': f"https://www.youtube.com/watch?v={video_id}"
        }
    
    @staticmethod
    def _extract_youtube_video_id(url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        parsed = urlparse(url)
        
        if parsed.hostname in ('youtu.be', 'www.youtu.be'):
            return parsed.path[1:]
        
        if parsed.hostname in ('youtube.com', 'www.youtube.com'):
            if parsed.path == '/watch':
                query = parse_qs(parsed.query)
                return query.get('v', [None])[0]
            elif parsed.path.startswith('/embed/'):
                return parsed.path.split('/')[2]
            elif parsed.path.startswith('/v/'):
                return parsed.path.split('/')[2]
        
        return None

    def _extract_aws(self, url: str) -> Dict[str, Any]:
        """Extract content from AWS blog post."""
        logger.info("Extracting AWS blog content")

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title = None
        content = None
        author = None
        published_date = None

        # Try meta tags first
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        meta_description = soup.find('meta', attrs={'name': 'description'})

        if og_title:
            title = og_title.get('content', '').strip()

        if og_description:
            content = og_description.get('content', '').strip()
        elif meta_description:
            content = meta_description.get('content', '').strip()

        # Try to extract from page structure
        if not title:
            # AWS blogs typically use h1 for the title
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text(strip=True)

        # Try to extract author from AWS blog structure
        # AWS blogs often have author info in specific classes
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            author = author_meta.get('content', '').strip()
        else:
            # Try to find author in common AWS blog patterns
            author_elem = soup.find('a', class_=re.compile(r'author'))
            if not author_elem:
                author_elem = soup.find('span', class_=re.compile(r'author'))
            if author_elem:
                author = author_elem.get_text(strip=True)

        # Try to extract publish date
        date_meta = soup.find('meta', property='article:published_time')
        if not date_meta:
            date_meta = soup.find('meta', attrs={'name': 'publish-date'})
        if date_meta:
            published_date = date_meta.get('content', '').strip()
        else:
            # Try to find date in page structure
            date_elem = soup.find('time')
            if date_elem:
                published_date = date_elem.get('datetime', '') or date_elem.get_text(strip=True)

        # Extract blog category from URL
        blog_category = None
        if '/blogs/' in url:
            parts = url.split('/blogs/')
            if len(parts) > 1:
                category_part = parts[1].split('/')[0]
                blog_category = category_part

        return {
            'platform': 'aws',
            'url': url,
            'title': title or 'AWS Blog Post',
            'content': content,
            'author': author,
            'published_date': published_date,
            'blog_category': blog_category,
            'raw_html': str(soup) if os.getenv('SAVE_RAW_HTML') == 'true' else None
        }

    def _extract_github(self, url: str) -> Dict[str, Any]:
        """Extract content from GitHub (repositories, issues, PRs, GitHub Pages)."""
        logger.info("Extracting GitHub content")

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Determine type: GitHub Pages or github.com
        is_github_pages = 'github.io' in domain
        content_type = 'github_pages' if is_github_pages else 'github'

        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        title = None
        content = None
        author = None
        repo_info = None

        # Try meta tags first
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        meta_description = soup.find('meta', attrs={'name': 'description'})

        if og_title:
            title = og_title.get('content', '').strip()

        if og_description:
            content = og_description.get('content', '').strip()
        elif meta_description:
            content = meta_description.get('content', '').strip()

        # Try to extract from page title if no meta tags
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)

        # For github.com URLs, try to extract repository info
        if not is_github_pages and 'github.com' in domain:
            # Extract repo owner and name from URL
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo_name = path_parts[1]
                repo_info = f"{owner}/{repo_name}"
                author = owner

                # Determine content type from URL structure
                if len(path_parts) > 2:
                    if path_parts[2] == 'issues':
                        content_type = 'github_issue'
                    elif path_parts[2] == 'pull':
                        content_type = 'github_pr'
                    elif path_parts[2] == 'discussions':
                        content_type = 'github_discussion'
                else:
                    content_type = 'github_repo'

        # For GitHub Pages, try to extract author from domain
        if is_github_pages:
            # Format: username.github.io
            subdomain = domain.split('.github.io')[0]
            if subdomain:
                author = subdomain

        # Try to find main content/description in page
        if not content:
            # Try to find README or main content
            readme = soup.find('article', class_=re.compile(r'markdown'))
            if readme:
                # Get first paragraph
                first_p = readme.find('p')
                if first_p:
                    content = first_p.get_text(strip=True)[:500]

        return {
            'platform': 'github',
            'content_type': content_type,
            'url': url,
            'title': title or 'GitHub Content',
            'content': content,
            'author': author,
            'repo_info': repo_info,
            'raw_html': str(soup) if os.getenv('SAVE_RAW_HTML') == 'true' else None
        }


def append_to_platform_csv(platform: str, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    """
    Append rows to a platform-specific CSV file at the TOP of the file.

    Args:
        platform: Platform name (linkedin, x, instagram, youtube)
        rows: List of rows to append
        fieldnames: CSV field names
    """
    if not rows:
        return

    csv_filename = f"{platform}.csv"
    existing_rows = []

    # Read existing rows if file exists
    if os.path.exists(csv_filename):
        with open(csv_filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)

    # Write new rows at the top, then existing rows
    with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)  # New rows first
        writer.writerows(existing_rows)  # Existing rows after

    logger.info(f"✓ Moved {len(rows)} row(s) to {csv_filename}")


def process_csv(
    csv_path: str,
    platform_filter: Optional[str] = None,
    force_all: bool = False,
    output_path: Optional[str] = None,
    move_completed: bool = True
) -> None:
    """
    Process URLs from a CSV file and update it with extracted data.

    Args:
        csv_path: Path to the CSV file containing URLs
        platform_filter: Optional platform filter ('linkedin', 'x', 'instagram', 'youtube')
        force_all: If True, process all rows. If False, only process rows where
                   title, author, and content are all empty
        output_path: Optional output path. If not provided, updates the input file
        move_completed: If True, move completed rows to platform-specific CSV files
    """
    extractor = SocialMediaExtractor()

    # Read the CSV file
    logger.info(f"Reading CSV file: {csv_path}")
    rows = []
    fieldnames = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        # Ensure required columns exist
        required_cols = ['url', 'title', 'author', 'content', 'platform']
        for col in required_cols:
            if col not in fieldnames:
                fieldnames.append(col)

        for row in reader:
            # Ensure all required columns exist in the row dict
            for col in required_cols:
                if col not in row:
                    row[col] = ''
            rows.append(row)

    logger.info(f"Loaded {len(rows)} rows from CSV")

    # Process each row
    processed_count = 0
    skipped_count = 0
    completed_rows = {
        'linkedin': [],
        'x': [],
        'instagram': [],
        'youtube': [],
        'aws': [],
        'github': []
    }
    remaining_rows = []

    for idx, row in enumerate(rows):
        url = row.get('url', '').strip()

        if not url:
            logger.debug(f"Row {idx + 1}: Skipping empty URL")
            skipped_count += 1
            remaining_rows.append(row)
            continue

        # Check platform filter
        if platform_filter:
            platform = extractor.get_platform(url)
            if platform != platform_filter.lower():
                logger.debug(f"Row {idx + 1}: Skipping {platform} URL (filter: {platform_filter})")
                skipped_count += 1
                remaining_rows.append(row)
                continue

        # Check if row should be processed (default: only if title, author, content are empty)
        should_process = force_all or (
            not (row.get('title') or '').strip() and
            not (row.get('author') or '').strip() and
            not (row.get('content') or '').strip()
        )

        if not should_process:
            logger.debug(f"Row {idx + 1}: Skipping non-empty row (use --force to process)")
            skipped_count += 1
            remaining_rows.append(row)
            continue

        # Extract data
        logger.info(f"Processing row {idx + 1}/{len(rows)}: {url}")
        try:
            result = extractor.extract(url)

            # Update row with extracted data
            row['platform'] = result.get('platform', '')
            row['title'] = result.get('title', '')
            row['author'] = result.get('author', '')
            row['content'] = result.get('content', '')

            processed_count += 1
            logger.info(f"  ✓ Extracted: {result.get('title', 'N/A')[:50]}")

            # Track completed rows by platform
            row_platform = row['platform']
            if move_completed and row_platform in completed_rows:
                completed_rows[row_platform].append(row)
            else:
                remaining_rows.append(row)

        except Exception as e:
            logger.error(f"  ✗ Failed to process row {idx + 1}: {e}")
            row['platform'] = 'error'
            row['title'] = ''
            row['author'] = ''
            row['content'] = f"Error: {str(e)}"
            remaining_rows.append(row)

    # Move completed rows to platform-specific CSV files
    if move_completed:
        # Determine which platforms to move
        platforms_to_move = []
        if platform_filter:
            platforms_to_move = [platform_filter]
        else:
            # Move all platforms that have completed rows
            platforms_to_move = [p for p in completed_rows.keys() if completed_rows[p]]

        for platform in platforms_to_move:
            if completed_rows[platform]:
                append_to_platform_csv(platform, completed_rows[platform], fieldnames)

    # Write remaining rows back to urls.csv
    output_file = output_path or csv_path
    logger.info(f"Writing remaining {len(remaining_rows)} row(s) to: {output_file}")

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(remaining_rows)

    logger.info(f"✓ Complete! Processed: {processed_count}, Skipped: {skipped_count}, Moved: {sum(len(rows) for rows in completed_rows.values())}")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description='Extract metadata and content from social media URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process urls.csv (extracts data and moves to platform CSVs)
  %(prog)s

  # Process a single URL
  %(prog)s https://linkedin.com/posts/...

  # Process only Instagram URLs (moves to instagram.csv)
  %(prog)s --platform instagram

  # Process only LinkedIn URLs (moves to linkedin.csv)
  %(prog)s --platform linkedin

  # Process all rows (including non-empty)
  %(prog)s --force

  # Keep completed rows in urls.csv (don't move)
  %(prog)s --no-move

Behavior:
  - By default, completed rows are moved to platform-specific CSV files
  - LinkedIn posts → linkedin.csv
  - X/Twitter posts → x.csv
  - Instagram posts → instagram.csv
  - YouTube videos → youtube.csv
  - AWS blogs → aws.csv
  - GitHub content → github.csv
  - New rows are added to the TOP of these files

Platforms:
  linkedin, x, instagram, youtube, aws, github
        """
    )

    parser.add_argument(
        'url',
        nargs='?',
        help='Single URL to process (if not provided, processes urls.csv by default)'
    )
    parser.add_argument(
        '--csv',
        type=str,
        default=None,
        help='Path to CSV file containing URLs (default: urls.csv if no URL provided)'
    )
    parser.add_argument(
        '--platform',
        type=str,
        choices=['linkedin', 'x', 'instagram', 'youtube', 'aws', 'github'],
        help='Filter by platform (only process URLs from this platform)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Process all rows, even if title/author/content already exist'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output CSV path (default: overwrite input file)'
    )
    parser.add_argument(
        '--no-move',
        action='store_true',
        help='Keep completed rows in urls.csv instead of moving to platform-specific files'
    )

    args = parser.parse_args()

    # Validate arguments and set defaults
    if args.url and args.csv:
        parser.error('Cannot process both a single URL and a CSV file simultaneously')

    # If no URL provided, default to processing urls.csv
    if not args.url:
        if args.csv is None:
            args.csv = 'urls.csv'

    # Process CSV file
    if args.csv:
        if not os.path.exists(args.csv):
            logger.error(f"CSV file not found: {args.csv}")
            return

        process_csv(
            csv_path=args.csv,
            platform_filter=args.platform,
            force_all=args.force,
            output_path=args.output,
            move_completed=not args.no_move
        )
        return

    # Process single URL
    if args.url:
        import json

        extractor = SocialMediaExtractor()
        logger.info(f"Extracting content from: {args.url}")

        try:
            result = extractor.extract(args.url)

            print(f"\n{'='*80}")
            print(f"Platform: {result.get('platform')}")
            print(f"URL: {result.get('url')}")
            print(f"Title: {result.get('title')}")
            print(f"Author: {result.get('author')}")
            print(f"Content Preview: {result.get('content', '')[:200]}...")
            print(f"{'='*80}\n")

            # Save to JSON
            output_file = 'extracted_content.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"Full result saved to {output_file}")

        except Exception as e:
            logger.error(f"Failed to process URL: {e}", exc_info=True)


if __name__ == '__main__':
    main()
