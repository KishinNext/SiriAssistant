from src.data.threads import get_the_last_thread
from src.data.core import DBSessionDep
from src.models.threads import ThreadsModel


async def get_thread(db_session: DBSessionDep) -> ThreadsModel:
    thread = await get_the_last_thread(db_session)
    return thread
