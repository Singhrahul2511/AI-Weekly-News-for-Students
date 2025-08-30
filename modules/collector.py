# modules/collector.py
import feedparser
import requests
from typing import List, Dict, Set
import logging
import os
from datetime import datetime, timedelta

# --- New: Add Tweepy for Twitter/X integration ---
# Make sure to run: pip install tweepy
# And add your bearer token to the .env file
import tweepy

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration for Content Sources ---
SOURCES = {
    "blogs": [
        "https://blog.google/technology/ai/rss/",
        "https://openai.com/blog/rss.xml",
        "https://blogs.nvidia.com/ai-podcast/feed/",
        "https://www.deepmind.com/blog/rss.xml",
    ],
    "research": "http://export.arxiv.org/rss/cs.AI",
    # --- New: Define influential X accounts to monitor ---
    "x_accounts": ["karpathy", "ylecun", "AndrewYNg", "sama"],
}

# --- New: Configure Tweepy API ---
try:
    twitter_client = tweepy.Client(settings.X_BEARER_TOKEN)
    X_AVAILABLE = True
except Exception as e:
    logger.warning(f"Could not configure X/Twitter API: {e}. X posts will be skipped.")
    X_AVAILABLE = False


def fetch_rss_feed(url: str, limit: int = 5) -> List[Dict]:
    """Fetches and parses an RSS feed."""
    items = []
    try:
        feed = feedparser.parse(url)
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
    # URL searches for topics:ai, sorts by stars, created in the last month
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    url = f"https://api.github.com/search/repositories?q=topic:artificial-intelligence+created:>{one_month_ago}&sort=stars&order=desc"

    try:
        # The official API requires a User-Agent header
        headers = {'User-Agent': 'AI-Newsletter-App'}
        response = requests.get(url, headers=headers, timeout=10)
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
def fetch_top_x_posts() -> List[Dict]:
    """Fetches recent, popular tweets from a list of influential accounts."""
    if not X_AVAILABLE:
        return []
    
    logger.info("Fetching top X posts...")
    all_tweets = []
    
    # Get tweets from the last 7 days
    start_time = datetime.utcnow() - timedelta(days=7)
    
    for username in SOURCES["x_accounts"]:
        try:
            user = twitter_client.get_user(username=username).data
            if user:
                tweets = twitter_client.get_users_tweets(
                    id=user.id,
                    max_results=5,
                    start_time=start_time,
                    tweet_fields=["public_metrics", "created_at"],
                    exclude=["replies", "retweets"]
                ).data
                
                if tweets:
                    for tweet in tweets:
                        all_tweets.append({
                            "source": "x",
                            "title": f"Post by @{username}",
                            "url": f"https://x.com/{username}/status/{tweet.id}",
                            "summary": tweet.text,
                            "metrics": tweet.public_metrics,
                        })
        except Exception as e:
            logger.error(f"Could not fetch tweets for {username}: {e}")

    # Sort tweets by a simple engagement metric (likes + retweets) and return top 5
    if not all_tweets:
        return []
        
    all_tweets.sort(key=lambda t: t['metrics'].get('like_count', 0) + t['metrics'].get('retweet_count', 0), reverse=True)
    return all_tweets[:5]


def collect_all_content() -> List[Dict]:
    """
    Collects content from all sources, deduplicates, and returns a clean list.
    """
    logger.info("Starting content collection...")
    
    # Fetch from all sources
    arxiv_papers = fetch_arxiv()
    blog_posts = fetch_blogs()
    github_repos = fetch_trending_github_repos()
    x_posts = fetch_top_x_posts()
    
    all_items = arxiv_papers + blog_posts + github_repos + x_posts
    
    # Deduplicate based on URL
    unique_items = []
    seen_urls: Set[str] = set()
    
    for item in all_items:
        if item.get("url") and item["url"] not in seen_urls:
            unique_items.append(item)
            seen_urls.add(item["url"])
            
    logger.info(f"Collected {len(unique_items)} unique items from all sources.")
    return unique_items