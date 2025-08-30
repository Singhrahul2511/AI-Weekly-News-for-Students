# modules/templater.py
import jinja2
from premailer import transform
from typing import Dict
import datetime

def render_newsletter(content: Dict) -> str:
    """
    Renders the newsletter HTML from a Jinja2 template with inlined CSS.
    
    Args:
        content: A dictionary with keys matching the newsletter sections.
    
    Returns:
        The full HTML string of the newsletter.
    """
    template_loader = jinja2.FileSystemLoader(searchpath="./templates")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("email_templates/newsletter.html.j2")
    
    # Prepare data for the template
    template_data = {
        "issue_date": datetime.date.today().strftime("%B %d, %Y"),
        "content": content
    }
    
    # Render the HTML
    html_body = template.render(template_data)
    
    # Inline CSS for better email client compatibility
    inlined_html = transform(html_body)
    
    return inlined_html