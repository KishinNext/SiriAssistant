import logging.config
from difflib import SequenceMatcher
from unittest.mock import patch

import pytest

from src.auth.spotify import get_spotify_client
from src.auth.utils import get_config, get_secrets
from src.models.functions import FunctionPayload, FunctionsAvailables
from src.service.functions import (
    open_pycharm_projects,
    play_spotify_music,
    search_specific_song,
    spotify_search
)
from src.tests.config_test import client

logging.basicConfig(level=logging.DEBUG)
config = get_config()
secrets = get_secrets()

# Set the pycharm_project variable with the name of the project you want to test
pycharm_project = None
open_spotify = True
sp_client = get_spotify_client()


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


@pytest.mark.parametrize("artist",
                         [
                             "Metallica",
                             "AC/DC",
                             "Led Zeppelin",
                             "Guns N' Roses",
                             "Rammstein",
                             "The Doors",
                             "The Who",
                             "Los Prisioneros",
                             "Caifanes",
                             "Molotov",
                             "Soda Stereo",
                             "Café Tacvba",
                             "Los Fabulosos Cadillacs",
                             "Los Auténticos Decadentes",
                             "Los Bunkers"
                         ]
                         )
def test_spotify_basic_search_artist(artist):
    query = f"artist: {artist}"
    result = spotify_search(sp_client, query)

    count = 0
    for first_artist in result['tracks']['items']:
        artist_result = first_artist['album']['artists'][0]['name']
        if SequenceMatcher(None, artist, artist_result).ratio() >= 0.7:
            count += 1

    percent = count / len(result['tracks']['items'])

    assert percent >= 0.7


def test_spotify_search_basic():
    result = spotify_search(sp_client, "test query")
    assert result is not None


def test_spotify_search_limit():
    result = spotify_search(sp_client, "test query", limit=5)
    assert len(result['tracks']['items']) == 5


@pytest.mark.asyncio
@pytest.mark.skipif(not open_spotify, reason="Manual test, set open_spotify to True to run")
async def test_play_spotify_music_general_search():
    params = FunctionPayload(
        thread_id="123",
        run_id="123",
        function_id="123",
        function_params={
            "spotify_search": "artist: Metallica",
            "artist_search": "Metallica",
            "song_search": "",
            "search_specific": False
        },
        function_name="play_spotify_music"
    )

    result = await play_spotify_music(func_params=params)

    # Verifica que el resultado sea el esperado
    assert result.function_id == '123'
    assert result.metadata == {}
    assert result.output['message'] == 'Successfully spotify opened'


@pytest.mark.parametrize("song",
                         [
                             'Uprising',
                             'Time',
                             'Starlight',
                             'Madness',
                             'Pressure',
                             'Psycho',
                             'Knights of Cydonia',
                             'Plug In Baby'
                         ]
                         )
def test_play_spotify_specific_song(song):
    query = f"track: {song}"
    result = spotify_search(sp_client, query)

    params = FunctionPayload(
        thread_id="123",
        run_id="123",
        function_id="123",
        function_params={},
        function_name="play_spotify_music"
    )
    search_specific_song_result = search_specific_song(
        search_result=result,
        song_search=song,
        artist_search='',
        func_params=params
    )
    assert search_specific_song_result['name'].lower() == song.lower()


def test_play_spotify_specific_song_and_artist():
    song = "Uprising"
    artist = "Muse"
    query = f"track: {song} artist: {artist}"
    result = spotify_search(sp_client, query)

    params = FunctionPayload(
        thread_id="123",
        run_id="123",
        function_id="123",
        function_params={},
        function_name="play_spotify_music"
    )
    search_specific_song_result = search_specific_song(
        search_result=result,
        song_search=song,
        artist_search=artist,
        func_params=params
    )
    assert search_specific_song_result['name'].lower() == song.lower()


@pytest.mark.asyncio
@pytest.mark.skipif(not open_spotify, reason="Manual test, set open_spotify to True to run")
async def test_play_spotify_music_specific_search():
    params = FunctionPayload(
        thread_id="123",
        run_id="123",
        function_id="123",
        function_params={
            "spotify_search": "artist: Muse track: Plug In Baby",
            "artist_search": "Muse",
            "song_search": "Plug In Baby",
            "search_specific": True
        },
        function_name="play_spotify_music"
    )

    result = await play_spotify_music(func_params=params)

    # Verifica que el resultado sea el esperado
    assert result.function_id == '123'
    assert result.metadata == {}
    assert result.output['message'] == 'Successfully spotify opened'
