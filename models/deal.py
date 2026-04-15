from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from db.database import Base

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prospect = Column(Text, nullable=False)
    conversation = Column(Text, nullable=False)  # stored as JSON string
    stage = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
