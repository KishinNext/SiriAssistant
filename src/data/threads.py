from datetime import datetime, timedelta, timezone

from openai import OpenAI
from sqlalchemy.sql import select

from src.auth.utils import get_config, get_secrets
from src.data.utils import db
from src.models.errors import Missing
from src.models.threads import ThreadsModel, ThreadsOrm

secrets = get_secrets()
config = get_config()
client = OpenAI(
    api_key=secrets['openai']['api_key'],
    timeout=60,
    max_retries=5
)


async def create(create_thread: ThreadsModel) -> ThreadsModel:
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

    async with db.session_scope() as session:
        session.add(thread_orm)
        return ThreadsModel.model_validate(thread_orm)


async def get_by_id(thread_id: str) -> ThreadsModel:
    async with db.session_scope() as session:
        query = select(ThreadsOrm).where(ThreadsOrm.id == thread_id)
        result = (await session.execute(query)).scalar_one_or_none()
        if result is None:
            raise Missing(msg=f"Thread {thread_id} not found")

        thread_data = ThreadsModel.model_validate(result)

    return thread_data


async def get_the_last_thread() -> ThreadsModel:
    async with db.session_scope() as session:
        query = select(ThreadsOrm).order_by(ThreadsOrm.created_at.desc()).limit(1)
        result = (await session.execute(query)).scalar_one_or_none()
        if result is None:
            create_result = await create(ThreadsModel())
            result = await get_by_id(create_result.id)

        thread_data = ThreadsModel.model_validate(result)
        if thread_data.expired_at < datetime.now(timezone.utc):
            create_result = await create(ThreadsModel())
            result = await get_by_id(create_result.id)
            thread_data = ThreadsModel.model_validate(result)

    return thread_data
