from pydantic import BaseModel
from typing import List, Optional


class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    track_ids: Optional[List[int]] = None

class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    track_ids: Optional[List[int]] = None


class PlaylistResponse(PlaylistBase):
    id: int
    owner_id: int
    track_ids: List[int] = []

    class Config:
        orm_mode = True
