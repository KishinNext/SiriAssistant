from enum import StrEnum

from pydantic import BaseModel, Field


class FunctionsAvailables(StrEnum):
    """
    Enum with the available functions
    """
    OPEN_PYCHARM_PROJECTS = "open_pycharm_projects"
    SEARCH_WEB = "search_web"


class FunctionPayload(BaseModel):
    thread_id: str = Field(..., description="Thread id")
    run_id: str = Field(..., description="Run id")
    function_id: str = Field(..., description="Function id given by OpenAI")
    function_params: dict = Field(..., description="Function params given by OpenAI")
    function_name: FunctionsAvailables = Field(..., description="Function name")


class FunctionResult(BaseModel):
    function_id: str = Field(..., description="Function id given by OpenAI")
    output: dict = Field(..., description="Function output message")
    metadata: dict | None = Field({}, description="Function metadata")
    traceback: str | None = Field(..., description="Function traceback if any error occurs")
