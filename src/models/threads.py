from datetime import datetime
from datetime import timedelta
from typing import Optional, Any

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, func, JSON, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ThreadsOrm(Base):
    __tablename__ = 'threads'
    __table_args__ = {'schema': 'openai'}

    id = Column(String, primary_key=True, nullable=False, unique=True)
    metadata_info = Column(JSON, nullable=True, default={})
    expired_at = Column(DateTime(timezone=True), nullable=False, default=func.now() + timedelta(minutes=30))
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class ThreadsModel(BaseModel):
    class Config:
        from_attributes = True

    id: Optional[str] = Field(None, example='356656427847206')
    metadata_info: dict | None = Field(None, example={"key": "value"})
    expired_at: datetime = Field(
        None,
        example='2021-09-01 00:30:00',
        description="The thread will expire after 10 minutes by default."
    )
    created_at: Optional[datetime] = Field(None, example='2021-09-01 00:00:00')
    updated_at: Optional[datetime] = Field(None, example='2021-09-01 00:00:00')
