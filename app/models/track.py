from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    duration = Column(Integer)

    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)

    album = relationship("Album", back_populates="tracks")
    playlists = relationship(
        "PlaylistTrack",
        back_populates="track",
        cascade="all, delete"
    )
