from pydantic import BaseModel
from typing import Optional


class ArtistBase(BaseModel):
    name: str
    genre: Optional[str] = None
    country: Optional[str] = None


class ArtistCreate(ArtistBase):
    pass


class ArtistResponse(ArtistBase):
    id: int

    class Config:
        orm_mode = True
