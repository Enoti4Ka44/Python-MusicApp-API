from pydantic import BaseModel
from typing import Optional

class TrackBase(BaseModel):
    title: str
    duration: Optional[int] = None

class TrackCreate(TrackBase):
    album_id: Optional[int] = None

class TrackResponse(TrackBase):
    id: int
    album_id: Optional[int]
    owner_id: int
    owner_name: str

    class Config:
        orm_mode = True
