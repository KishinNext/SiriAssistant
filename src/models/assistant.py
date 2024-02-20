from pydantic import BaseModel, Field


class AssistantModel(BaseModel):
    id: str = Field(..., description="Message id")
    name: str = Field(..., description="name of the assistant")

