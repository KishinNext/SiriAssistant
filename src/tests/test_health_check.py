import logging.config

import pytest

from src.auth.utils import get_config, get_secrets
from src.tests.config_test import client

logging.basicConfig(level=logging.DEBUG)
config = get_config()
secrets = get_secrets()


@pytest.mark.asyncio
async def test_playground(client):
    token = secrets['api_tokens']['token']
    response = await client.get(
        '/health-check',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
