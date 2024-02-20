from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ResponseSchema(BaseModel):
    status_code: int = Field(..., description="Status code")
    content: dict = Field(..., description="Message")
    timestamp: str = Field(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), description="Timestamp")
    metadata: Optional[dict] = Field(None, description="Metadata")


class ErrorResponseSchema(BaseModel):
    status_code: int = Field(..., description="Status code")
    message: str = Field(..., description="Message")
    timestamp: str = Field(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), description="Timestamp")
    metadata: Optional[dict] = Field(None, description="Metadata")
    error_code: Optional[int] = Field(None, description="Error code")
    traceback: Optional[str] = Field(None, description="Traceback")
