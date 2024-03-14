import logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
from spotipy.cache_handler import MemoryCacheHandler
from src.auth.utils import get_secrets

secrets = get_secrets()


def get_spotify_client() -> spotipy.Spotify | None:
    access_token = get_spotify_oauth_client().get('access_token')
    if access_token is None:
        return None

    spotify_client = spotipy.Spotify(access_token)

    smart_check_xd = spotify_client.current_user_playlists()

    return spotipy.Spotify(access_token)


def get_spotify_oauth_client() -> dict | None:
    try:
        oauth_client = SpotifyOAuth(
            client_id=secrets['spotify']['client_id'],
            client_secret=secrets['spotify']['client_secret'],
            redirect_uri=secrets['spotify']['redirect_uri'],
            scope=secrets['spotify']['scope'],
            cache_handler=MemoryCacheHandler()
        )

        if oauth_client.is_token_expired(oauth_client.get_access_token()):
            return oauth_client.refresh_access_token(oauth_client.get_access_token()['refresh_token'])

        return oauth_client.get_access_token()
    except SpotifyOauthError as e:
        logging.warning(f"Error in get_spotify_oauth_client: {e}")
        return None
