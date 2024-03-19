from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, func, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SpotifyTokensOrm(Base):
    __tablename__ = 'tokens'
    __table_args__ = {'schema': 'openai'}

    access_token = Column(String, primary_key=True, nullable=False, unique=True)
    refresh_token = Column(String, nullable=True)
    token_type = Column(String, nullable=True)
    expires_in = Column(Numeric, nullable=True)
    scope = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())


class SpotifyTokensModel(BaseModel):
    class Config:
        from_attributes = True

    access_token: str = Field(None, example='BQD0X5H3V8i9u1m5e3')
    refresh_token: str = Field(None, example='BQD0X3V8i9u1m5e3')
    token_type: str = Field(None, example='bearer')
    expires_in: int = Field(None, example=3600)
    scope: str = Field(None, example='user-read-private')
    expires_at: datetime = Field(None, example='2021-09-01 00:00:00')
    created_at: Optional[datetime] = Field(None, example='2021-09-01 00:00:00')
    updated_at: Optional[datetime] = Field(None, example='2021-09-01 00:00:00')
