from sqlalchemy import Column, String, Integer
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # store Supabase user id here
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    age = Column(Integer, nullable=True)

