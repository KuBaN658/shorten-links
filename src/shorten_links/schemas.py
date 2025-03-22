from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from config import settings


class ShortenLinkCreate(BaseModel):
    url: str
    lifetime_seconds: int = settings.life_time_links.default_with_clicks
    description: str
    alias: Optional[str] = None
    project: Optional[str] = None


class UrlUpdate(BaseModel):
    url: str


class Stats(BaseModel):
    original_url: str
    created_at: datetime
    clicks: int
    last_clicked_at: Optional[datetime]
