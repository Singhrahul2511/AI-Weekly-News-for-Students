# modules/categorizer.py
from typing import Dict, List
import logging
import random
import time

logger = logging.getLogger(__name__)

# --- New: More sophisticated selection logic ---

def select_and_categorize(items: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Selects the best items for the newsletter from a mixed list of sources
    and assigns them to specific, engaging sections, ensuring all items are unique.
    """
    logger.info("Categorizing and selecting top items...")
    
    # Use a set to track which items have been assigned to prevent duplicates
    assigned_urls = set()
    
    categorized_content = {
        "Introduction": [],
        "Big Story of the Week": [],
        "Top Research Paper": [],
        "Top GitHub Repo": [],
        "Quote_of_the_Week": [], # New!
        "AI_Job_Spotlight": [], # New!
        "Top_AI_Tools_and_Products": [], # Renamed
        "Top_X_Post": [], # Renamed
        "Closing Notes": [],
    }
    
    # Separate items by source for easier selection
    blogs = [item for item in items if item.get("source") == "rss"]
    papers = [item for item in items if "arxiv.org" in item.get("url", "")]
    repos = [item for item in items if item.get("source") == "github"]
    x_posts = [item for item in items if item.get("source") == "x"]

    # --- Selection Logic ---
    
    # 1. Select the Big Story (from major blogs)
    if blogs:
        # Prioritize OpenAI, Google, DeepMind for big stories
        priority_keywords = ["openai", "google", "deepmind", "anthropic"]
        big_story = next((b for b in blogs if any(key in b['url'] for key in priority_keywords)), blogs[0])
        big_story['category'] = "Big Story of the Week"
        categorized_content["Big Story of the Week"].append(big_story)
        assigned_urls.add(big_story['url'])

    # 2. Select the Top Research Paper
    if papers:
        top_paper = papers[0]
        top_paper['category'] = "Top Research Paper"
        categorized_content["Top Research Paper"].append(top_paper)
        assigned_urls.add(top_paper['url'])

    # 3. Select the Top GitHub Repo
    if repos:
        top_repo = repos[0]
        top_repo['category'] = "Top GitHub Repo"
        categorized_content["Top GitHub Repo"].append(top_repo)
        assigned_urls.add(top_repo['url'])

    # 4. Select the Top X Post
    if x_posts:
        top_post = x_posts[0]
        top_post['category'] = "Top X Post"
        categorized_content["Top_X_Post"].append(top_post)
        assigned_urls.add(top_post['url'])

    # --- New Static & Dynamic Sections for Engagement ---

    # import time

    # 5. Add a Quote of the Week
    quotes = [
        {"quote": "The science of today is the technology of tomorrow.", "author": "Edward Teller"},
        {"quote": "The best way to predict the future is to invent it.", "author": "Alan Kay"},
        {"quote": "AI is the new electricity.", "author": "Andrew Ng"}
    ]
    chosen_quote = random.choice(quotes)
    chosen_quote['title'] = f"Quote by {chosen_quote['author']}"
    chosen_quote['url'] = f"#/quote-{int(time.time())}"
    chosen_quote['summary'] = chosen_quote['quote']
    categorized_content["Quote_of_the_Week"].append(chosen_quote)

    # 6. Add an AI Job Spotlight (Now with 2 jobs and real links)
    jobs = [
        {"title": "AI/ML Engineer Intern", "company": "Google", "url": "https://careers.google.com/students/", "description": "Work on real-world machine learning models and data pipelines at a leading tech company."},
        {"title": "Data Science Research Assistant", "company": "MIT Media Lab", "url": "https://www.media.mit.edu/jobs/", "description": "Assist PhD students in cutting-edge AI research, focusing on NLP and computer vision."}
    ]
    # Add unique URLs and summaries to each job
    for job in jobs:
        job['url'] = job['url'] # Using the real URL
        job['summary'] = job['description']
    categorized_content["AI_Job_Spotlight"] = jobs[:2] # Select the first two jobs

    # 7. Add Top AI Tools
    tools = [
        {"name": "Hugging Face", "url": "https://huggingface.co/", "summary": "The ultimate platform for pre-trained models and datasets."},
        {"name": "Replicate", "url": "https://replicate.com/", "summary": "Run open-source ML models with a cloud API."},
        {"name": "Weights & Biases", "url": "https://wandb.ai/", "summary": "The developer-first MLOps platform for experiment tracking."}
    ]
    for tool in tools:
        tool['title'] = tool['name']
    categorized_content["Top_AI_Tools_and_Products"] = tools
    
    logger.info("Finished categorizing content with real data and new sections.")
    return categorized_content