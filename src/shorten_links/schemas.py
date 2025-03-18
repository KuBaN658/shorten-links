from typing import Optional
from pydantic import BaseModel


class ShortenLinkCreate(BaseModel):
    url: str
    lifetime_minutes: int
    description: str
    alias: Optional[str] = None

