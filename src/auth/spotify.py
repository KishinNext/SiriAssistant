import logging
from datetime import datetime, timezone

import spotipy
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError

from src.auth.utils import get_secrets
from src.data.spotify import create
from src.data.spotify import get_the_last_token
from src.models.spotify import SpotifyTokensModel

secrets = get_secrets()


async def get_spotify_client() -> spotipy.Spotify | None:
    last_token = await get_the_last_token()
    access_token = last_token.access_token

    if access_token is None:
        return None
    elif last_token.expires_at < datetime.now(timezone.utc):
        access_token = await refresh_access_token(last_token.refresh_token)

    spotify_client = spotipy.Spotify(access_token)

    smart_check_xd = spotify_client.current_user_playlists()

    return spotify_client


async def refresh_access_token(refresh_token: str) -> str:
    oauth_client = SpotifyOAuth(
        client_id=secrets['spotify']['client_id'],
        client_secret=secrets['spotify']['client_secret'],
        redirect_uri=secrets['spotify']['redirect_uri'],
        scope=secrets['spotify']['scope'],
        cache_handler=MemoryCacheHandler()
    )

    new_token_info = oauth_client.refresh_access_token(refresh_token)
    await create(token_info=SpotifyTokensModel(**new_token_info))

    return new_token_info['access_token']


def get_spotify_oauth_client() -> dict | None:
    try:
        oauth_client = SpotifyOAuth(
            client_id=secrets['spotify']['client_id'],
            client_secret=secrets['spotify']['client_secret'],
            redirect_uri=secrets['spotify']['redirect_uri'],
            scope=secrets['spotify']['scope'],
            cache_handler=MemoryCacheHandler()
        )

        access_token = oauth_client.get_access_token()

        if oauth_client.is_token_expired(access_token):
            new_token_info = oauth_client.refresh_access_token(access_token['refresh_token'])
            return new_token_info

        return access_token
    except SpotifyOauthError as e:
        logging.warning(f"Error in get_spotify_oauth_client: {e}")
        return None
