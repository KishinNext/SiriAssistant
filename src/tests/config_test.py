from async_asgi_testclient import TestClient
from src.main import app
import pytest_asyncio
import pytest


@pytest_asyncio.fixture(scope="function")
@pytest.mark.asyncio
async def client():
    async with TestClient(app) as client:
        yield client
