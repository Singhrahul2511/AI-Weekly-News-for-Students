# web/models.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import datetime

# Pydantic models for API request/response validation

class SubscriberBase(BaseModel):
    email: EmailStr

class Subscriber(SubscriberBase):
    id: int
    is_active: bool
    subscribed_at: datetime.datetime

    class Config:
        from_attributes = True

class Issue(BaseModel):
    id: int
    subject: str
    created_at: datetime.datetime
    sent_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True