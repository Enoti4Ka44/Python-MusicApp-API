from pydantic import BaseModel
from typing import Optional


class AlbumBase(BaseModel):
    title: str
    release_year: Optional[int] = None


class AlbumCreate(AlbumBase):
    artist_id: int


class AlbumResponse(AlbumBase):
    id: int
    artist_id: int

    class Config:
        orm_mode = True
