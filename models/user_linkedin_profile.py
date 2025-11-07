from sqlalchemy import Column, String, TIMESTAMP, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base




class UserLinkedInProfile(Base):
    __tablename__ = "user_linkedin_profile"

    user_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    linkedin_profile_url = Column(String(512), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "linkedin_profile_url", name="user_linkedin_profile_unique"),
        Index("idx_user_linkedin_profile_user_id", "user_id"),
    )
