# modules/storage.py
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from typing import List, Optional, Set

from config import settings

# Setup SQLAlchemy
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- ORM Models ---

class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    subscribed_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    content_html = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    mailchimp_campaign_id = Column(String, nullable=True)
    items = relationship("NewsletterItem", back_populates="issue")

class NewsletterItem(Base):
    __tablename__ = "newsletter_items"
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    summary = Column(Text, nullable=False)
    category = Column(String, nullable=False) # e.g., Big Story, Research, Repo
    issue = relationship("Issue", back_populates="items")

Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Provides a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- New helper function ---
def get_existing_urls(db_session) -> Set[str]:
    """Fetches a set of all URLs currently in the newsletter_items table."""
    urls = db_session.query(NewsletterItem.url).all()
    return {url for (url,) in urls}


# --- Database CRUD Functions ---

def add_subscriber(email: str) -> Optional[Subscriber]:
    with get_db() as db:
        try:
            db_subscriber = Subscriber(email=email)
            db.add(db_subscriber)
            db.commit()
            db.refresh(db_subscriber)
            return db_subscriber
        except IntegrityError:
            db.rollback()
            return None # Email already exists

def get_subscriber(email: str) -> Optional[Subscriber]:
    with get_db() as db:
        return db.query(Subscriber).filter(Subscriber.email == email).first()

def get_all_active_subscribers() -> List[Subscriber]:
    with get_db() as db:
        return db.query(Subscriber).filter(Subscriber.is_active == True).all()

def unsubscribe_subscriber(email: str) -> bool:
    with get_db() as db:
        subscriber = db.query(Subscriber).filter(Subscriber.email == email).first()
        if subscriber:
            subscriber.is_active = False
            db.commit()
            return True
        return False

# --- Improved save_issue function ---
def save_issue(subject: str, content_html: str, items: list, mailchimp_id: Optional[str] = None) -> Issue:
    with get_db() as db:
        # First, create and save the main issue entry
        new_issue = Issue(
            subject=subject,
            content_html=content_html,
            mailchimp_campaign_id=mailchimp_id,
            sent_at=datetime.datetime.utcnow() if mailchimp_id else None
        )
        db.add(new_issue)
        db.flush()  # This assigns an ID to new_issue without committing the transaction

        # Get a set of all URLs that are already in the database
        existing_urls = get_existing_urls(db)

        # Now, only add items with new URLs
        for item_data in items:
            # Skip items that are not dictionaries or are empty
            if not isinstance(item_data, dict) or not item_data:
                continue

            item_url = item_data.get('url', '#')
            
            # If the URL is already in the database, skip this item
            if item_url in existing_urls:
                continue

            # Gracefully get data, providing default values if keys are missing
            db_item = NewsletterItem(
                issue_id=new_issue.id,
                title=item_data.get('title', item_data.get('name', 'Untitled')),
                url=item_url,
                summary=item_data.get('summary', item_data.get('description', '')),
                category=item_data.get('category', 'General')
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(new_issue)
        return new_issue

def get_last_issue() -> Optional[Issue]:
    with get_db() as db:
        return db.query(Issue).order_by(Issue.created_at.desc()).first()