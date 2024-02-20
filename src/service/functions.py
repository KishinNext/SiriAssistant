import difflib
import logging
import os
import re

from src.auth.utils import get_secrets
from src.models.functions import FunctionPayload, FunctionResult, FunctionsAvailables
from src.service.openai import client

secrets = get_secrets()


def find_top_project_matches(input_str: str, folders_info: dict, top=3) -> dict:
    if input_str in folders_info:
        return {input_str: folders_info[input_str]}

    close_names = difflib.get_close_matches(input_str.lower(), folders_info.keys(), n=top, cutoff=0.5)

    closest_matches = {}
    for name in close_names:
        closest_matches[name] = folders_info[name]

    return closest_matches


async def return_output_functions(
        func_payload: FunctionPayload,
        **kwargs: dict
) -> FunctionResult:
    if func_payload.function_name == FunctionsAvailables.OPEN_PYCHARM_PROJECTS:
        result_function = await open_pycharm_projects(func_payload, **kwargs)
    else:
        raise Exception(f"Function {func_payload.function_name} not found")
    return result_function


async def open_pycharm_projects(func_params: FunctionPayload, **kwargs: dict) -> FunctionResult:
    try:
        project_paths = secrets['pycharm_directories']
        pycharm_project = func_params.function_params.get('pycharm_project', None)

        if pycharm_project is None:
            raise Exception('The pycharm_project is required')

        all_folders = {}
        for project in project_paths:
            for name in os.listdir(project):
                if os.path.isdir(os.path.join(project, name)) and not re.match(r'^\..+', name):
                    if name in all_folders:
                        all_folders[name].append(os.path.join(project, name))
                    else:
                        all_folders[name] = [os.path.join(project, name)]

        matches = find_top_project_matches(pycharm_project, all_folders)

        if not matches:
            raise Exception(f'No project found for {pycharm_project}')

        if len(list(matches.keys())) == 1:
            message = f'Opening pycharm project {list(matches.keys())[0]} successfully.'

            os.system(f'pycharm {list(matches.values())[0][0]}')

        else:
            message = f'Found multiple projects for {pycharm_project}, please be more specific. Here is the the nearest' \
                      f' matches: {list(matches.keys())}'

        return FunctionResult(
            function_id=func_params.function_id,
            output={'message': message},
            metadata={},
            traceback=None
        )
    except Exception as e:
        client.beta.threads.runs.cancel(
            thread_id=func_params.thread_id,
            run_id=func_params.run_id
        )
        logging.error(f"Error in open_pycharm_projects: {e}, the run function es closed")
        return FunctionResult(
            function_id=func_params.function_id,
            output={'message': 'Error in open_pycharm_projects'},
            metadata={},
            traceback=str(e)
        )
