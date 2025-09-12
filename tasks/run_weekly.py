# tasks/run_weekly.py
import argparse
import logging
import os
import random
from typing import Dict, List
import time
from modules.collector import collect_all_content
from modules.summarizer import get_summary
from modules.categorizer import select_and_categorize
from modules.templater import render_newsletter
from modules.mailer import get_mailer
from modules.storage import save_issue
from config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_subject_line(big_story_title: str) -> str:
    """Generates a compelling subject line."""
    variants = [
        f"🤖 AI Weekly News: {big_story_title}",
        f"Your Weekly AI Briefing: {big_story_title} & More",
        f"This Week in AI: {big_story_title}",
    ]
    return random.choice(variants)

def orchestrate_newsletter_creation(dry_run: bool = True, send_test_email_first: bool = True, admin_email: str = None):
    """
    Full pipeline: Collect -> Summarize -> Categorize -> Render -> Send/Save
    """
    logging.info("Starting newsletter creation pipeline...")

    # 1. Collect
    raw_content = collect_all_content()
    if not raw_content:
        logging.warning("No content collected. Aborting.")
        return

    # Shuffle the content to ensure a variety of items are summarized
    random.shuffle(raw_content)

    # 2. Summarize (only a subset to save API calls)
    summarized_content = []
    # Create a dictionary for quick lookups of summaries
    summaries = {}
    for item in raw_content[:6]: # Summarize only the first 6 items
        try:
            summary = get_summary(item)
            # Store the summary with the URL as the key
            if item.get("url"):
                summaries[item["url"]] = summary
            time.sleep(4)
        except Exception as e:
            logging.error(f"Could not get summary for '{item['title']}': {e}")
    
    # --- THIS IS THE CRITICAL FIX ---
    # Now, add summaries to the full list of content
    for item in raw_content:
        if item.get("url") and item["url"] in summaries:
            item["summary"] = summaries[item["url"]]
    # --- END OF FIX ---

    # 3. Categorize and Select from the FULL list of content
    final_content = select_and_categorize(raw_content) # Use raw_content, not summarized_content
    
    if not final_content or not any(final_content.values()):
        logging.error("Categorization failed or resulted in no content. Aborting newsletter generation.")
        return

    # 4. Generate Subject Line
    big_story_list = final_content.get("Big Story of the Week", [])
    big_story = big_story_list[0] if big_story_list else {"title": "The Latest in AI"}
    subject = generate_subject_line(big_story['title'])
    preview_text = big_story.get('summary', 'Your weekly update on the world of Artificial Intelligence.')

    # 5. Render HTML
    html_output = render_newsletter(final_content)

    if dry_run:
        if not os.path.exists("out"):
            os.makedirs("out")
        with open("out/last_preview.html", "w", encoding="utf-8") as f:
            f.write(html_output)
        logging.info("Dry run complete. Newsletter saved to out/last_preview.html")
        
        all_items = [item for sublist in final_content.values() for item in sublist]
        unique_items = list({item['url']: item for item in all_items if item.get('url')}.values())
        save_issue(subject, html_output, items=unique_items)
        return

    # --- Live Send Logic ---
    logging.info("Starting live send process...")
    mailer = get_mailer()
    
    campaign_id = mailer.create_campaign(subject, preview_text)
    if not campaign_id:
        logging.error("Failed to create Mailchimp campaign. Aborting send.")
        return

    if not mailer.set_campaign_content(campaign_id, html_output):
        logging.error("Failed to set campaign content. Aborting send.")
        return
        
    if not dry_run and send_test_email_first and admin_email:
        if not mailer.send_test_email(campaign_id, admin_email):
            logging.error(f"Failed to send test email to {admin_email}. Aborting live send.")
            return
        logging.info(f"Test email sent successfully to {admin_email}. Proceeding with main send in 10 seconds...")
        time.sleep(10)

    if mailer.send_campaign(campaign_id):
        logging.info("Campaign sent successfully!")
        all_items = [item for sublist in final_content.values() for item in sublist]
        unique_items = list({item['url']: item for item in all_items if item.get('url')}.values())
        save_issue(subject, html_output, unique_items, mailchimp_id=campaign_id)
    else:
        logging.error("Failed to send campaign to the main list.")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AI Weekly Newsletter pipeline.")
    parser.add_argument("--dry-run", action="store_true", help="Generate HTML preview without sending emails.")
    parser.add_argument("--send", action="store_true", help="Send the newsletter to the mailing list.")
    parser.add_argument("--test-email", type=str, default=settings.ADMIN_EMAIL, help="Email address to send a test to before the main send.")
    args = parser.parse_args()

    if args.send:
        orchestrate_newsletter_creation(dry_run=False)
    elif args.dry_run:
        orchestrate_newsletter_creation(dry_run=True)
    else:
        print("Please specify either --dry-run or --send.")