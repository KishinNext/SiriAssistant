import logging.config

import pytest

from src.auth.utils import get_config, get_secrets
from src.models.assistant_selector import AssistantSelectorModel, Message
from src.tests.config_test import client

logging.basicConfig(level=logging.DEBUG)
config = get_config()
secrets = get_secrets()
manual_test = False


@pytest.mark.order(1)
@pytest.mark.skipif(not secrets['openai']['api_key'] and manual_test, reason='missing openai_config credentials')
@pytest.mark.asyncio
async def test_conversational_tool(client):
    payload = AssistantSelectorModel(
        messages=[
            Message(role='user', content='Hello, how can you help me?')
        ]
    )

    token = secrets['api_tokens']['token']
    response = await client.post(
        '/assistant_selector',
        headers={'Authorization': f'Bearer {token}'},
        json=payload.model_dump()
    )
    assert response.status_code == 200
    assert response.json()['content']['conversation_closed'] == 'False'


@pytest.mark.order(2)
@pytest.mark.skipif(not secrets['openai']['api_key'] and manual_test, reason='missing openai_config credentials')
@pytest.mark.asyncio
async def test_conversational_tool_close_conversation(client):
    payload = AssistantSelectorModel(
        messages=[
            Message(role='user', content="I don't need more help")
        ]
    )

    token = secrets['api_tokens']['token']
    response = await client.post(
        '/assistant_selector',
        headers={'Authorization': f'Bearer {token}'},
        json=payload.model_dump()
    )
    assert response.status_code == 200
    assert response.json()['content']['conversation_closed'] == 'True'


@pytest.mark.order(3)
@pytest.mark.skipif(not secrets['openai']['api_key'] and manual_test, reason='missing openai_config credentials')
@pytest.mark.asyncio
async def test_pycharm_function(client):
    payload = AssistantSelectorModel(
        messages=[
            Message(role='user', content="open the pycharm project gptvision")
        ]
    )

    token = secrets['api_tokens']['token']
    response = await client.post(
        '/assistant_selector',
        headers={'Authorization': f'Bearer {token}'},
        json=payload.model_dump()
    )
    assert response.status_code == 200
    assert response.json()['content']['conversation_closed'] == 'True'


@pytest.mark.order(4)
@pytest.mark.skipif(not secrets['openai']['api_key'] and manual_test, reason='missing openai_config credentials')
@pytest.mark.asyncio
async def test_spotify_general_function(client):
    payload = AssistantSelectorModel(
        messages=[
            Message(role='user', content="play something of muse on spotify ")
        ]
    )

    token = secrets['api_tokens']['token']
    response = await client.post(
        '/assistant_selector',
        headers={'Authorization': f'Bearer {token}'},
        json=payload.model_dump()
    )
    assert response.status_code == 200
