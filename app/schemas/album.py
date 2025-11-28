from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class AlbumBase(BaseModel):
    title: str

class AlbumCreate(AlbumBase):
    pass

class AlbumResponse(AlbumBase):
    id: int
    release_date: date
    owner_id: int
    owner_name: str
    track_ids: List[int] = []

    class Config:
        orm_mode = True
