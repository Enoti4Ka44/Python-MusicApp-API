from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    genre = Column(String(50))

    albums = relationship("Album", back_populates="artist")
