from openai import OpenAI

from src.auth.utils import get_config, get_secrets

secrets = get_secrets()
config = get_config()

client = OpenAI(
    api_key=secrets['openai']['api_key'],
    organization=secrets['openai']['organization'],
    timeout=60,
    max_retries=5
)
