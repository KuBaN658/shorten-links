from fastapi import APIRouter

from src.shorten_links.schemas import ShortenLinkCreate
from src.shorten_links.crud import add_shorten_link

router = APIRouter()

@router.post("/shorten")
async def shorten_link(shorten_link: ShortenLinkCreate):
    return await add_shorten_link(shorten_link)
