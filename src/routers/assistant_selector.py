import logging
from datetime import datetime
from src.data.core import DBSessionDep
from fastapi import APIRouter, Depends

from src.auth.service import api_key_auth
from src.models.assistant_selector import AssistantSelectorModel
from src.models.response import ErrorResponseSchema, ResponseSchema
from src.service import assistant_selector as service

router = APIRouter(
    prefix="/assistant_selector",
    tags=["assistant_selector"],
)


@router.post(
    "",
    response_model=ResponseSchema,
    response_model_exclude_none=False,
    dependencies=[Depends(api_key_auth)]
)
async def get_all(
        payload: AssistantSelectorModel,
        db_session: DBSessionDep,
) -> ResponseSchema | ErrorResponseSchema:
    try:
        result = await service.post_messages(db_session, payload)
        logging.info(result)
        return ResponseSchema(
            status_code=200,
            content=result['content'],
            metadata={
                "role": result['role'],
                "created_at": result['created_at'],
                "run_id": result['run_id'],
                "thread_id": result['thread_id']
            },
            timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )
    except Exception as e:
        logging.error(e)
        return ErrorResponseSchema(
            status_code=500,
            message="failed to get response from assistant",
            error_code=500,
            traceback=str(e),
            timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )
