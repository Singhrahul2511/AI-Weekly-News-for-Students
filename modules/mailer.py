# modules/mailer.py
import requests
import logging
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

class MailchimpMailer:
    def __init__(self):
        self.api_key = settings.MAILCHIMP_API_KEY
        self.server_prefix = settings.MAILCHIMP_SERVER_PREFIX
        self.list_id = settings.MAILCHIMP_LIST_ID
        self.api_url = f"https://{self.server_prefix}.api.mailchimp.com/3.0"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"apikey {self.api_key}"
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            # This is the new, fixed code
            response.raise_for_status()
            if response.status_code == 204:
                return {}  # Return an empty dictionary for success with no content
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Mailchimp API error for {method} {endpoint}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise
            
    def create_campaign(self, subject: str, preview_text: str) -> Optional[str]:
        """Creates a new campaign in Mailchimp and returns its ID."""
        logger.info("Creating Mailchimp campaign...")
        data = {
            "type": "regular",
            "recipients": {
                "list_id": self.list_id
            },
            "settings": {
                "subject_line": subject,
                "preview_text": preview_text,
                "from_name": settings.MAILCHIMP_FROM_NAME,
                "reply_to": settings.MAILCHIMP_REPLY_TO
            }
        }
        response = self._make_request("POST", "campaigns", data)
        campaign_id = response.get("id")
        logger.info(f"Campaign created with ID: {campaign_id}")
        return campaign_id

    def set_campaign_content(self, campaign_id: str, html_content: str) -> bool:
        """Sets the HTML content for a given campaign."""
        logger.info(f"Setting content for campaign {campaign_id}...")
        data = {"html": html_content}
        endpoint = f"campaigns/{campaign_id}/content"
        try:
            self._make_request("PUT", endpoint, data)
            logger.info("Campaign content set successfully.")
            return True
        except Exception:
            return False

    def send_test_email(self, campaign_id: str, test_email: str) -> bool:
        """Sends a test email for a campaign."""
        logger.info(f"Sending test email for campaign {campaign_id} to {test_email}...")
        data = {
            "test_emails": [test_email],
            "send_type": "html"
        }
        endpoint = f"campaigns/{campaign_id}/actions/test"
        try:
            self._make_request("POST", endpoint, data)
            logger.info("Test email sent successfully.")
            return True
        except Exception:
            return False

    def send_campaign(self, campaign_id: str) -> bool:
        """Sends the campaign to the entire list."""
        logger.info(f"Sending campaign {campaign_id} to list {self.list_id}...")
        endpoint = f"campaigns/{campaign_id}/actions/send"
        try:
            self._make_request("POST", endpoint)
            logger.info("Campaign sent successfully!")
            return True
        except Exception:
            return False

def get_mailer():
    """Factory function to get a mailer instance."""
    return MailchimpMailer()