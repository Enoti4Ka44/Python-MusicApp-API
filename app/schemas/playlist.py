from pydantic import BaseModel
from typing import List, Optional


class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    owner_id: int
    track_ids: Optional[List[int]] = None


class PlaylistOut(PlaylistBase):
    id: int
    owner_id: int
    track_ids: List[int] = []

    class Config:
        orm_mode = True
