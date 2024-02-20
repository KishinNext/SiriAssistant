from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field("user", description="Role could be user or assistant")
    content: str = Field("Hi, my name is KishinNext", description="Message content")


class AssistantSelectorModel(BaseModel):
    messages: list[Message] = Field(..., description="List of messages")
