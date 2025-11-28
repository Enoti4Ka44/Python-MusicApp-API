from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.user import User
from datetime import date

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    release_date = Column(Date, default=date.today)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="albums") 
    tracks = relationship("Track", back_populates="album")