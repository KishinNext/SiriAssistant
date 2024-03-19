from datetime import datetime, timezone

from openai import OpenAI
from sqlalchemy.sql import select

from src.auth.utils import get_config, get_secrets
from src.data.utils import db
from src.models.spotify import SpotifyTokensModel, SpotifyTokensOrm

secrets = get_secrets()
config = get_config()
client = OpenAI(
    api_key=secrets['openai']['api_key'],
    timeout=60,
    max_retries=5
)


async def create(token_info: SpotifyTokensModel) -> SpotifyTokensModel:
    sp_orm = SpotifyTokensOrm(**token_info.model_dump())

    async with db.session_scope() as session:
        session.add(sp_orm)
        return SpotifyTokensModel.model_validate(sp_orm)


async def get_the_last_token() -> SpotifyTokensModel:
    async with db.session_scope() as session:
        query = select(SpotifyTokensOrm).order_by(SpotifyTokensOrm.created_at.desc()).limit(1)
        result = (await session.execute(query)).scalar_one_or_none()
        token_info = SpotifyTokensModel.model_validate(result)

    return token_info
