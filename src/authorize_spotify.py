import asyncio
from datetime import datetime, timezone

from src.auth.spotify import get_spotify_oauth_client
from src.data.spotify import create
from src.models.spotify import SpotifyTokensModel


def get_spotify_access_token():
    try:
        oauth_token = get_spotify_oauth_client()
        return SpotifyTokensModel(
            access_token=oauth_token['access_token'],
            token_type=oauth_token['token_type'],
            expires_in=oauth_token['expires_in'],
            refresh_token=oauth_token['refresh_token'],
            scope=oauth_token['scope'],
            expires_at=datetime.fromtimestamp(oauth_token['expires_at'], timezone.utc)
        )
    except Exception as e:
        print(f'Error in get_spotify_access_token: {e}')
        return None


async def main():
    spotify_token_model = get_spotify_access_token()
    if spotify_token_model:
        await create(spotify_token_model)
        print('Token successfully obtained and stored!!!.')
    else:
        print('Error obtaining token.')


if __name__ == '__main__':
    asyncio.run(main())
