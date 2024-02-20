import src.data.threads as threads
from src.models.threads import ThreadsModel


async def get_thread() -> ThreadsModel:
    thread = await threads.get_the_last_thread()
    return thread
