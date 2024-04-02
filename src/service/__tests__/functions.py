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
open_spotify = False

# TODO: Run multiple tests breaks the database connection, need to fix it,
#  for now, run the tests one by one, posible problem is related with context manager

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


@pytest.mark.asyncio
async def test_spotify_basic_search_artist():
    artists = [
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

    failed_artists = []
    sp_client = await get_spotify_client()

    for artist in artists:
        query = f"artist: {artist}"
        result = spotify_search(sp_client, query)

        count = 0
        for first_artist in result['tracks']['items']:
            artist_result = first_artist['album']['artists'][0]['name']
            if SequenceMatcher(None, artist, artist_result).ratio() >= 0.7:
                count += 1

        percent = count / len(result['tracks']['items']) if result['tracks']['items'] else 0

        if percent < 0.7:
            failed_artists.append(artist)

    assert not failed_artists, f"Failed artists: {', '.join(failed_artists)}"


@pytest.mark.asyncio
async def test_spotify_search_basic():
    sp_client = await get_spotify_client()
    result = spotify_search(sp_client, "test query")
    assert result is not None


@pytest.mark.asyncio
async def test_spotify_search_limit():
    sp_client = await get_spotify_client()
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


@pytest.mark.asyncio
async def test_play_spotify_specific_song():
    songs = [
        'Uprising',
        'Time',
        'Starlight',
        'Madness',
        'Pressure',
        'Psycho',
        'Plug In Baby'
    ]

    failed_songs = []
    sp_client = await get_spotify_client()

    for song in songs:
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

        # Verificar que el nombre de la canción coincida, ignorando mayúsculas/minúsculas
        if search_specific_song_result['name'].lower() != song.lower():
            failed_songs.append(song)

    assert not failed_songs, f"Failed songs: {', '.join(failed_songs)}"


@pytest.mark.asyncio
async def test_play_spotify_specific_song_and_artist():
    sp_client = await get_spotify_client()
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
