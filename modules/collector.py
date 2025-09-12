# modules/collector.py
import feedparser
import requests
from requests.adapters import HTTPAdapter, Retry
from typing import List, Dict, Set
import logging
import os
from datetime import datetime, timedelta
import tweepy
from config import settings
# We need BeautifulSoup to parse the HTML
from bs4 import BeautifulSoup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- New: Create a resilient requests session ---
# This session will act like a browser and automatically retry failed requests
# --- New: Create a more resilient requests session ---
session = requests.Session()
# This header makes our script look like a regular Chrome browser
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive"
})
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

# --- Configuration for Content Sources ---
# modules/collector.py

# --- Configuration for Content Sources ---

SOURCES = {
    "blogs": [
        "https://blog.google/technology/ai/rss/",
        "https://openai.com/blog/rss.xml",
        "https://aws.amazon.com/blogs/machine-learning/feed/",
        "https://www.livemint.com/rss/technology",
        "https://timesofindia.indiatimes.com/rssfeeds/50730332.cms",
        # The problematic Product Hunt URL has been removed.
    ],
    "research": "http://export.arxiv.org/rss/cs.AI",
    "jobs": "https://weworkremotely.com/categories/remote-programming-jobs.rss", # <-- ADD THIS NEW KEY
}

def fetch_rss_feed(url: str, limit: int = 5) -> List[Dict]:
    """Fetches and parses an RSS feed using our resilient session."""
    items = []
    try:
        # Using feedparser's ability to take a file-like object
        response = session.get(url, timeout=15)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        
        for entry in feed.entries[:limit]:
            items.append({
                "source": "rss",
                "title": entry.title,
                "url": entry.link,
                "summary": entry.get("summary", ""),
                "published": entry.get("published_parsed")
            })
    except Exception as e:
        logger.error(f"Failed to fetch RSS feed {url}: {e}")
    return items

def fetch_arxiv() -> List[Dict]:
    """Fetches latest from arXiv AI feed."""
    return fetch_rss_feed(SOURCES["research"], limit=10)

def fetch_blogs() -> List[Dict]:
    """Fetches latest from configured blog RSS feeds."""
    all_blog_posts = []
    for url in SOURCES["blogs"]:
        all_blog_posts.extend(fetch_rss_feed(url, limit=5))
    return all_blog_posts

def fetch_trending_github_repos() -> List[Dict]:
    """Fetches trending AI repositories directly from GitHub's API."""
    logger.info("Fetching trending GitHub repos from official API...")
    items = []
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    url = f"https://api.github.com/search/repositories?q=topic:artificial-intelligence+created:>{one_month_ago}&sort=stars&order=desc"
    
    try:
        # Using the same resilient session headers
        headers = session.headers.copy()
        github_token = settings.GITHUB_PAT
        if github_token:
            headers['Authorization'] = f"token {github_token}"
        
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        for repo in response.json().get("items", [])[:5]:
            items.append({
                "source": "github",
                "title": repo.get("full_name"),
                "url": repo.get("html_url"),
                "summary": repo.get("description", "No description provided."),
            })
    except Exception as e:
        logger.error(f"Failed to fetch GitHub repos: {e}")
    return items

# modules/collector.py

def collect_all_content() -> List[Dict]:
    logger.info("Starting content collection...")

    arxiv_papers = fetch_arxiv()
    blog_posts = fetch_blogs()
    github_repos = fetch_trending_github_repos()
    ai_jobs = fetch_jobs_rss() # <-- CHANGE THIS LINE

    all_items = arxiv_papers + blog_posts + github_repos + ai_jobs

    # ... (the rest of the function remains the same)
    
    unique_items = []
    seen_urls: Set[str] = set()
    
    for item in all_items:
        if item.get("url") and item["url"] not in seen_urls:
            unique_items.append(item)
            seen_urls.add(item["url"])
            
    logger.info(f"Collected {len(unique_items)} unique items from all sources.")
    return unique_items

# modules/collector.py
# modules/collector.py

def fetch_jobs_rss() -> List[Dict]:
    """Fetches latest from the remote jobs RSS feed."""
    return fetch_rss_feed(SOURCES["jobs"], limit=5)

# Add this new function at the end of the file
def fetch_ai_jobs() -> List[Dict]:
    """Scrapes a job board for the latest AI/ML jobs suitable for students."""
    logger.info("Fetching AI jobs...")
    items = []
    url = "https://www.entrylevel.io/jobs?j=machine+learning"
    
    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # --- THIS IS THE UPDATED PART ---
        # The website has changed its HTML classes. These are the latest ones.
        job_listings = soup.find_all('div', class_='JobCard_jobCard__E6221', limit=3)
        
        for job in job_listings:
            title_element = job.find('h3', class_='JobCard_jobTitle__sType8')
            company_element = job.find('p', class_='JobCard_companyName__3Gj26')
            link_element = job.find('a', class_='JobCard_jobCardLink__x_fGT')
        # --- END OF UPDATED PART ---
            
            if title_element and company_element and link_element:
                items.append({
                    "source": "job_board",
                    "title": title_element.get_text(strip=True),
                    "company": company_element.get_text(strip=True),
                    "url": "https://www.entrylevel.io" + link_element['href'],
                    "description": f"An exciting opportunity at {company_element.get_text(strip=True)}."
                })
    except Exception as e:
        logger.error(f"Failed to fetch AI jobs: {e}")
    return items