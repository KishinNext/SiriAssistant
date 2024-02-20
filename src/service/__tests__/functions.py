import logging.config
from unittest.mock import patch

import pytest

from src.auth.utils import get_config, get_secrets
from src.models.functions import FunctionPayload, FunctionsAvailables
from src.service.functions import open_pycharm_projects
from src.tests.config_test import client

logging.basicConfig(level=logging.DEBUG)
config = get_config()
secrets = get_secrets()
# Set the pycharm_project variable with the name of the project you want to test
pycharm_project = None


@pytest.mark.asyncio
@pytest.mark.skipif(pycharm_project is None or pycharm_project == '',
                    reason="Pycharm project name for test is not set in the pycharm_project variable")
async def test_open_pycharm_projects(client):
    payload = FunctionPayload(
        thread_id='123',
        run_id='123',
        function_id='123',
        function_params={'pycharm_project': pycharm_project},
        function_name=FunctionsAvailables.OPEN_PYCHARM_PROJECTS
    )

    with patch('os.system') as mock_os_system:
        result = await open_pycharm_projects(payload)
        mock_os_system.assert_called()
