# modules/categorizer.py
from typing import Dict, List
import logging
import random
import time

logger = logging.getLogger(__name__)

# modules/categorizer.py

def select_and_categorize(items: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Selects and categorizes items for the newsletter with a final, robust logic
    to ensure all sections are populated correctly.
    """
    logger.info("Categorizing and selecting top items...")

    # --- Step 1: Initialize categories and a set to track used URLs ---
    assigned_urls = set()
    categorized_content = {
        "Big Story of the Week": [],
        "Indian_AI_News": [],
        "Top Research Paper": [],
        "Top GitHub Repo": [],
        "AI_Job_Spotlight": [],
        "Quote_of_the_Week": [],
    }

    # --- Step 2: Correctly separate all items into exclusive lists ---
    papers = [item for item in items if "arxiv.org" in item.get("url", "")]
    repos = [item for item in items if item.get("source") == "github"]
    jobs = [item for item in items if "weworkremotely.com" in item.get("url", "")]
    
    all_blogs = [
        item for item in items 
        if item.get("source") == "rss" 
        and "arxiv.org" not in item.get("url", "")
        and "weworkremotely.com" not in item.get("url", "")
    ]

    indian_news_urls = ["livemint.com", "timesofindia.indiatimes.com"]
    indian_news = []
    general_blogs = []
    for blog in all_blogs:
        if any(url in blog.get("url", "") for url in indian_news_urls):
            indian_news.append(blog)
        else:
            general_blogs.append(blog)

    # --- Step 3: Define a helper function to safely add items ---
    def add_item(section, item_list, max_items=1):
        added_count = 0
        for item in item_list:
            if item.get('url') and item['url'] not in assigned_urls and added_count < max_items:
                categorized_content[section].append(item)
                assigned_urls.add(item['url'])
                added_count += 1

    # --- Step 4: Fill categories with priority content first ---
    priority_keywords = ["openai", "google", "deepmind", "anthropic", "aws"]
    priority_blogs = [b for b in general_blogs if any(key in b.get('url', '') for key in priority_keywords)]
    
    add_item("Big Story of the Week", priority_blogs)
    add_item("Indian_AI_News", indian_news, 2)
    add_item("Top Research Paper", papers)
    add_item("Top GitHub Repo", repos)

    # --- Step 5: Use Fallbacks to fill any remaining empty sections ---
    remaining_blogs = [b for b in general_blogs if b.get('url') and b['url'] not in assigned_urls]
    remaining_papers = [p for p in papers if p.get('url') and p['url'] not in assigned_urls]

    if not categorized_content["Big Story of the Week"]:
        add_item("Big Story of the Week", remaining_blogs)
    if not categorized_content["Indian_AI_News"]:
        add_item("Indian_AI_News", remaining_blogs, 2)
    if not categorized_content["Top Research Paper"]:
        add_item("Top Research Paper", remaining_papers)

    # --- Step 6: Add static and job sections ---
    if jobs:
        formatted_jobs = []
        for job in jobs[:2]:
            parts = job['title'].split(':', 1)
            company = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else "Software Engineer"
            formatted_jobs.append({
                "title": title, "company": company, "url": job['url'], "description": job['summary']
            })
        categorized_content["AI_Job_Spotlight"] = formatted_jobs

    # --- THIS IS THE UPDATED QUOTES LIST ---
    quotes = [
        {"quote": "The science of today is the technology of tomorrow.", "author": "Edward Teller"},
        {"quote": "The best way to predict the future is to invent it.", "author": "Alan Kay"},
        {"quote": "AI is the new electricity.", "author": "Andrew Ng"},
        {"quote": "Success in creating AI would be the biggest event in human history. Unfortunately, it might also be the last.", "author": "Stephen Hawking"},
        {"quote": "The real problem is not whether machines think but whether men do.", "author": "B.F. Skinner"},
        {"quote": "Anything that could give rise to smarter-than-human intelligence—in the form of AI, brain-computer interfaces, or neuroscience-based human intelligence enhancement—wins hands down beyond contest as doing the most to change the world.", "author": "Eliezer Yudkowsky"},
        {"quote": "The development of full artificial intelligence could spell the end of the human race.", "author": "Stephen Hawking"},
        {"quote": "Machine intelligence is the last invention that humanity will ever need to make.", "author": "Nick Bostrom"},
        {"quote": "I am telling you, the world’s first trillionaires are going to come from somebody who masters AI and all its derivatives and applies it in ways we never thought of.", "author": "Mark Cuban"},
        {"quote": "Some people call this artificial intelligence, but the reality is this technology will enhance us. So instead of artificial intelligence, I think we'll augment our intelligence.", "author": "Ginni Rometty"},
        {"quote": "The question of whether a computer can think is no more interesting than the question of whether a submarine can swim.", "author": "Edsger W. Dijkstra"},
        {"quote": "Artificial intelligence is growing up fast, as are robots whose facial expressions can elicit empathy and make your mirror neurons quiver.", "author": "Diane Ackerman"},
        {"quote": "It seems probable that once the machine thinking method had started, it would not take long to outstrip our feeble powers.", "author": "Alan Turing"},
        {"quote": "By far, the greatest danger of Artificial Intelligence is that people conclude too early that they understand it.", "author": "Eliezer Yudkowsky"},
        {"quote": "What I'm trying to do is the sensitive task of wrapping AI in a rational, humanistic ethics.", "author": "Fei-Fei Li"},
        {"quote": "The key to artificial intelligence has always been the representation.", "author": "Jeff Hawkins"},
        {"quote": "The pace of progress in artificial intelligence is incredibly fast. Unless you have direct exposure to groups like Deepmind, you have no idea how fast—it is growing at a pace close to exponential.", "author": "Elon Musk"},
        {"quote": "We are entering a new world. The technologies of machine learning, speech recognition, and natural language understanding are reaching a nexus of capability.", "author": "Jeff Bezos"},
        {"quote": "If you invent a breakthrough in artificial intelligence, so machines can learn, that is worth 10 Microsofts.", "author": "Bill Gates"},
        {"quote": "Data is the new oil? No, data is the new soil.", "author": "David McCandless"},
        {"quote": "In the long run, I think we will evolve in partnership with our machinery.", "author": "Kevin Kelly"},
        {"quote": "Everything we love about civilization is a product of intelligence, so amplifying our human intelligence with artificial intelligence has the potential of helping civilization flourish like never before.", "author": "Max Tegmark"},
    ]
    chosen_quote = random.choice(quotes)
    # The URL needs to be unique for the database, but the title and summary can be from the chosen quote
    chosen_quote['url'] = f"#/quote-{int(time.time())}"
    categorized_content["Quote_of_the_Week"].append(chosen_quote)

    logger.info("Finished categorizing content with final robust logic.")
    return categorized_content