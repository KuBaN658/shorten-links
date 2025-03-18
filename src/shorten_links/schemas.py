from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ShortenLinkCreate(BaseModel):
    url: str
    lifetime_minutes: int = 60
    description: str
    alias: Optional[str] = None


class Stats(BaseModel):
    original_url: str
    created_at: datetime
    clicks: int
    last_clicked_at: Optional[datetime]
