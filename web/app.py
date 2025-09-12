# web/app.py
from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from modules.mailer import get_mailer
from modules.storage import add_subscriber, get_all_active_subscribers, get_last_issue, Subscriber as DBSubscriber, get_db
from web.models import Subscriber, Issue
from config import settings
from tasks.run_weekly import orchestrate_newsletter_creation
# Add these imports at the top of web/app.py
from fastapi import BackgroundTasks

app = FastAPI(title="AI Newsletter Service")

# Mount static files (for CSS, JS, etc.) and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/static")

# --- Helper Functions ---
def verify_admin_token(token: str):
    """Dependency to verify the admin token."""
    if token != settings.ADMIN_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")

# --- Frontend Routes ---

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def read_root(request: Request):
    # Always pass success and error so the template always renders correctly
    return templates.TemplateResponse("index.html", {"request": request, "success": None, "error": None})

# web/app.py

@app.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def handle_subscribe(request: Request, email: str = Form(...)):
    """Handles new subscriber submissions."""
    if not email:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Email is required."})

    new_subscriber = add_subscriber(email)
    if new_subscriber is None:
        return templates.TemplateResponse("index.html", {"request": request, "error": f"{email} is already subscribed."})

    # --- ADD THIS NEW CODE ---
    # Now, also add the subscriber to Mailchimp
    mailer = get_mailer()
    mailer.add_subscriber_to_list(email)
    # --- END OF NEW CODE ---

    return templates.TemplateResponse("index.html", {"request": request, "success": f"Thanks for subscribing, {email}!"})
    
@app.get("/last", response_class=HTMLResponse)
async def view_last_issue():
    """Displays the HTML of the most recently sent newsletter."""
    issue = get_last_issue()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No issues found.")
    return HTMLResponse(content=issue.content_html)

# --- Admin Routes ---

# web/app.py

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, token: str):
    """
    A professional admin dashboard protected by a query token.
    Shows subscribers and allows triggering a test send.
    """
    verify_admin_token(token)
    subscribers = get_all_active_subscribers()
    return templates.TemplateResponse(
        "admin.html", 
        {
            "request": request, 
            "subscribers": subscribers,
            "token": token
        }
    )

@app.post("/admin/trigger_dry_run")
async def trigger_dry_run(token: str = Form(...)):
    """Endpoint for the cron job or admin to trigger a newsletter dry run."""
    verify_admin_token(token)
    try:
        orchestrate_newsletter_creation(dry_run=True)
        return RedirectResponse(url=f"/admin?token={token}", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# # Add these imports at the top of web/app.py
# from fastapi import BackgroundTasks

# Add this new function somewhere before the new endpoint
def run_newsletter_task():
    """Wrapper function to run the newsletter orchestration."""
    # We are calling the function with default arguments (send=True, test_email=ADMIN_EMAIL)
    # Note: For a real production system, you might pass these as parameters
    from tasks.run_weekly import orchestrate_newsletter_creation
    from config import settings
    
    # Setting dry_run=False sends the real email
    orchestrate_newsletter_creation(dry_run=False, send_test_email_first=True, admin_email=settings.ADMIN_EMAIL)

# Add this new endpoint at the end of web/app.py
@app.post("/tasks/run-weekly-job")
async def trigger_weekly_job(token: str, background_tasks: BackgroundTasks):
    """
    A secure endpoint to be called by an external scheduler (like GitHub Actions).
    It runs the newsletter creation and sending process in the background.
    """
    # Verify the secret token to ensure only authorized services can run the job
    verify_admin_token(token)
    
    # Add the long-running task to the background
    background_tasks.add_task(run_newsletter_task)
    
    # Immediately return a response to the scheduler
    return {"message": "Weekly newsletter job has been triggered successfully in the background."}