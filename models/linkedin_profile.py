from sqlalchemy import Column, String, JSON, TIMESTAMP, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from database import Base

class LinkedInProfile(Base):
    __tablename__ = "linkedin_profile"

    profile_url = Column(String(512), primary_key=True)
    profile_data = Column(JSONB, nullable=False)
    profile_report_data = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())