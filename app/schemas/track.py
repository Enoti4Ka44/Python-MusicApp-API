from pydantic import BaseModel
from typing import Optional


class TrackBase(BaseModel):
    title: str
    duration: Optional[int] = None


class TrackCreate(TrackBase):
    album_id: int


class TrackResponse(TrackBase):
    id: int
    album_id: int

    class Config:
        orm_mode = True
