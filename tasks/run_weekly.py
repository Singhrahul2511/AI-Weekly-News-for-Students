# tasks/run_weekly.py
import argparse
import logging
import os
import random
from typing import Dict, List

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

def orchestrate_newsletter_creation(dry_run: bool = True):
    """
    Full pipeline: Collect -> Summarize -> Categorize -> Render -> Send/Save
    """
    logging.info("Starting newsletter creation pipeline...")

    # 1. Collect
    raw_content = collect_all_content()
    if not raw_content:
        logging.warning("No content collected. Aborting.")
        return

    # 2. Summarize (only a subset to save API calls)
    summarized_content = []
    for item in raw_content[:15]: # Limit summarization
        try:
            summary = get_summary(item)
            item_with_summary = {**item, "summary": summary}
            summarized_content.append(item_with_summary)
        except Exception as e:
            logging.error(f"Failed to summarize '{item['title']}': {e}")
    
    # 3. Categorize and Select
    final_content = select_and_categorize(summarized_content)
    
    # 4. Generate Subject Line
    big_story = final_content["Big Story of the Week"][0] if final_content["Big Story of the Week"] else {"title": "The Latest in AI"}
    subject = generate_subject_line(big_story['title'])
    # This is more robust. It provides a default value if 'summary' is missing.
    preview_text = big_story.get('summary', 'The latest updates in the world of AI.')

    # 5. Render HTML
    html_output = render_newsletter(final_content)

    if dry_run:
        # Save preview to file
        if not os.path.exists("out"):
            os.makedirs("out")
        with open("out/last_preview.html", "w", encoding="utf-8") as f:
            f.write(html_output)
        logging.info("Dry run complete. Newsletter saved to out/last_preview.html")
        save_issue(subject, html_output, items=[item for sublist in final_content.values() for item in sublist])
        return

    # --- Live Send Logic ---
    logging.info("Starting live send process...")
    mailer = get_mailer()
    
    # Create campaign
    campaign_id = mailer.create_campaign(subject, preview_text)
    if not campaign_id:
        logging.error("Failed to create Mailchimp campaign. Aborting send.")
        return

    # Set content
    if not mailer.set_campaign_content(campaign_id, html_output):
        logging.error("Failed to set campaign content. Aborting send.")
        return
        
    # Send test email
    if args.test_email:
        if not mailer.send_test_email(campaign_id, args.test_email):
            logging.error("Failed to send test email. Aborting live send.")
            return
        input(f"Test email sent to {args.test_email}. Press Enter to confirm and send to the main list...")

    # Send to main list
    if mailer.send_campaign(campaign_id):
        logging.info("Campaign sent successfully!")
        # Save sent issue to DB
        all_items = [item for sublist in final_content.values() for item in sublist]
        save_issue(subject, html_output, all_items, mailchimp_id=campaign_id)
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