from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    release_year = Column(Integer)

    artist_id = Column(Integer, ForeignKey("artists.id"), nullable=False)

    artist = relationship("Artist", back_populates="albums")
    tracks = relationship("Track", back_populates="album")
