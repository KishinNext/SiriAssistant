import difflib
import logging
import os
import random
import re
import webbrowser
import webbrowser as web
from difflib import SequenceMatcher
from time import sleep

import keyboard
import spotipy

from src.auth.spotify import get_spotify_client
from src.auth.utils import get_secrets
from src.models.functions import FunctionPayload, FunctionResult, FunctionsAvailables

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
    elif func_payload.function_name == FunctionsAvailables.SEARCH_WEB:
        result_function = await search_web(func_payload, **kwargs)
    elif func_payload.function_name == FunctionsAvailables.PLAY_SPOTIFY_MUSIC:
        result_function = await play_spotify_music(func_payload, **kwargs)
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

        if len(list(matches.keys())) == 1:
            message = f'Opening pycharm project {list(matches.keys())[0]} successfully.'

            os.system(f'pycharm {list(matches.values())[0][0]}')

        elif len(list(matches.keys())) > 1:
            message = f'Found multiple projects for {pycharm_project}, please be more specific. Here is the the nearest' \
                      f' matches: {list(matches.keys())}'
        else:
            message = f'No project found for {pycharm_project}'

        return FunctionResult(
            function_id=func_params.function_id,
            output={'message': message},
            metadata={},
            traceback=None
        )
    except Exception as e:
        # client.beta.threads.runs.cancel(
        #     thread_id=func_params.thread_id,
        #     run_id=func_params.run_id
        # )
        logging.error(f"Error in open_pycharm_projects: {e}, the run function es closed")
        return FunctionResult(
            function_id=func_params.function_id,
            output={'message': 'Error in open_pycharm_projects'},
            metadata={},
            traceback=str(e)
        )


async def search_web(func_params: FunctionPayload, **kwargs: dict) -> FunctionResult:
    try:
        url = func_params.function_params.get('url', None)

        webbrowser.open(url, new=1, autoraise=True)

        return FunctionResult(
            function_id=func_params.function_id,
            output={'message': 'Successfully opened the browser'},
            metadata={},
            traceback=None
        )
    except Exception as e:
        # client.beta.threads.runs.cancel(
        #     thread_id=func_params.thread_id,
        #     run_id=func_params.run_id
        # )
        logging.error(f"Error in search_web: {e}, the run function es closed")
        return FunctionResult(
            function_id=func_params.function_id,
            output={'message': 'Fail to open in the browser'},
            metadata={},
            traceback=str(e)
        )


def spotify_search(client: spotipy.Spotify, query: str, limit: int = 10):
    search_result = client.search(query, limit=limit, type='track')
    return search_result


def search_specific_song(
        search_result: dict,
        song_search: str,
        func_params: FunctionPayload,
        artist_search: str
) -> FunctionResult | dict:
    searched_list = []

    for type in search_result.keys():
        info_type = search_result[type]['items']

        if artist_search != '':
            filter_info = list(
                filter(lambda x:
                       SequenceMatcher(None, artist_search, x['album']['artists'][0]['name']).ratio() >= 0.6
                       and SequenceMatcher(None, song_search, x['name']).ratio() >= 0.6,
                       info_type
                       )
            )
        else:
            filter_info = list(
                filter(lambda x:
                       SequenceMatcher(None, song_search, x['name']).ratio() >= 0.6,
                       info_type
                       )
            )

        searched_list.extend(filter_info)

    if len(searched_list) == 0:
        return FunctionResult(
            function_id=func_params.function_id,
            output={'message': 'No search results found for the query'},
            metadata={},
            traceback=None
        )

    ordered_list = sorted(searched_list, key=lambda x: x.get('popularity', 0), reverse=True)[0]

    return ordered_list


async def play_spotify_music(func_params: FunctionPayload, **kwargs: dict) -> FunctionResult:
    try:
        sp_client = get_spotify_client()
        if sp_client is None:
            return FunctionResult(
                function_id=func_params.function_id,
                output={'message': 'The spotify client is not available, '
                                   'you need to login first or get the credentials '
                                   'configured in the development.yaml file'},
                metadata={},
                traceback=None
            )

        sp_search = func_params.function_params.get('spotify_search', '')
        artist_search = func_params.function_params.get('artist_search', '')
        song_search = func_params.function_params.get('song_search', '')

        search_result = spotify_search(sp_client, sp_search)

        if func_params.function_params.get('search_specific') is False:
            # could filter the search result to get the best match (?)
            random_number = random.randint(0, len(search_result["tracks"]["items"]) - 1)
            web.open(search_result["tracks"]["items"][random_number]["uri"])

            if sp_client.current_playback() is not None:
                if sp_client.current_playback()['is_playing']:
                    # if you have the spotify premium you can use this
                    # sp_client.start_playback(search_result["tracks"]["items"][random_number]["uri"])
                    sleep(1)
                    keyboard.press_and_release("enter")

        else:

            ordered_list = search_specific_song(
                search_result=search_result,
                song_search=song_search,
                artist_search=artist_search,
                func_params=func_params
            )

            if isinstance(ordered_list, FunctionResult):
                return ordered_list

            web.open(ordered_list["uri"])

            if sp_client.current_playback() is not None:
                if sp_client.current_playback()['is_playing']:
                    # if you have the spotify premium you can use this
                    # sp_client.start_playback(search_result["tracks"]["items"][random_number]["uri"])
                    sleep(1)
                    keyboard.press_and_release("enter")

        return FunctionResult(
            function_id=func_params.function_id,
            output={'message': 'Successfully spotify opened'},
            metadata={},
            traceback=None
        )
    except Exception as e:
        # client.beta.threads.runs.cancel(
        #     thread_id=func_params.thread_id,
        #     run_id=func_params.run_id
        # )
        logging.error(f"Error in play_music: {e}, the run function es closed")
        return FunctionResult(
            function_id=func_params.function_id,
            output={'message': 'Fail to open in spotify'},
            metadata={},
            traceback=str(e)
        )
