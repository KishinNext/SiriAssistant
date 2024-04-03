from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from src.auth.openai import client
from src.auth.utils import get_config, get_secrets
from src.models.errors import Missing
from src.models.threads import ThreadsModel, ThreadsOrm

secrets = get_secrets()
config = get_config()


async def create(db_session: AsyncSession, create_thread: ThreadsModel) -> ThreadsModel:
    create_thread = client.beta.threads.create(
        metadata=create_thread.metadata_info
    )
    create_thread = create_thread.model_dump()

    thread_info = {
        "id": create_thread['id'],
        "metadata": create_thread['metadata'],
        "expired_at": (datetime.now(timezone.utc) + timedelta(minutes=config['threads']['expiration'])),
        "created_at": datetime.fromtimestamp(create_thread['created_at'], timezone.utc)
    }

    thread_orm = ThreadsOrm(**thread_info)

    db_session.add(thread_orm)
    return ThreadsModel.model_validate(thread_orm)


async def get_by_id(db_session: AsyncSession, thread_id: str) -> ThreadsModel:
    query = select(ThreadsOrm).where(ThreadsOrm.id == thread_id)
    result = (await db_session.execute(query)).scalar_one_or_none()
    if result is None:
        raise Missing(msg=f"Thread {thread_id} not found")

    thread_data = ThreadsModel.model_validate(result)

    return thread_data


async def get_the_last_thread(db_session: AsyncSession) -> ThreadsModel:
    query = select(ThreadsOrm).order_by(ThreadsOrm.created_at.desc()).limit(1)
    result = (await db_session.execute(query)).scalar_one_or_none()
    if result is None:
        create_result = await create(db_session, ThreadsModel())
        result = await get_by_id(db_session, create_result.id)

    thread_data = ThreadsModel.model_validate(result)
    if thread_data.expired_at < datetime.now(timezone.utc):
        create_result = await create(db_session, ThreadsModel())
        result = await get_by_id(db_session, create_result.id)
        thread_data = ThreadsModel.model_validate(result)

    return thread_data
