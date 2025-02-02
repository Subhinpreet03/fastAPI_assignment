from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100), nullable=True)
    bio = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    photo_url = Column(String(255), nullable=True)
