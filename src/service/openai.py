from openai import OpenAI

from src.models.assistant import AssistantModel
from src.auth.utils import get_config, get_secrets

secrets = get_secrets()
config = get_config()

client = OpenAI(
    api_key=secrets['openai']['api_key'],
    timeout=60,
    max_retries=5
)


def list_available_assistants() -> list[dict[str, str]]:
    all_assistants = client.beta.assistants.list(
        order="desc",
        limit=30,
    )

    assistants_names = []
    for assistant in all_assistants.data:
        assistants_names.append({
            "name": assistant.name,
            "id": assistant.id
        })

    return assistants_names


def get_assistants() -> dict[str, AssistantModel]:

    available_assistants = {assistant['name']: assistant for assistant in list_available_assistants()}
    selected_assistants = {}

    for assistant in config['assistants']:
        if assistant['name'] in available_assistants:
            selected_assistants = {
                assistant['name']: AssistantModel(**available_assistants[assistant['name']])
            }
        else:
            raise ValueError(f"Assistant {assistant['name']} not found")

    if not selected_assistants:
        raise ValueError(f"Assistants {config['assistants']} not found")

    return selected_assistants
