from sqlalchemy import Column, String, Integer
from database import Base

class UserQuery(Base):
    __tablename__ = "query"

    id = Column(String,primary_key=True)
    count = Column(Integer)