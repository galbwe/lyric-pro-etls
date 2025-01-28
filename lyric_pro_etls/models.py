from datetime import datetime

from pydantic import BaseModel


class Song(BaseModel):
    slug: str
    title: str
    artist: str
    lyrics: str
    release_date: datetime | None = None
    about: str | None = None
