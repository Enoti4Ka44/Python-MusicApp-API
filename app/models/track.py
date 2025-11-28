from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user import User

class Track(Base):
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    duration = Column(Integer)
    album_id = Column(Integer, ForeignKey("albums.id", ondelete="SET NULL"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # автор

    album = relationship("Album", back_populates="tracks")
    owner = relationship("User")
    playlists = relationship(
        "PlaylistTrack",
        back_populates="track",
        cascade="all, delete"
    )
