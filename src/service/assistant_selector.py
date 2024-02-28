import json
import logging
import re
from datetime import datetime

from src.models.assistant_selector import AssistantSelectorModel
from src.models.functions import FunctionPayload
from src.service.functions import return_output_functions
from src.service.openai import client
from src.service.openai import get_assistants
from src.service.threads import get_thread


async def post_messages(messages: AssistantSelectorModel):
    thread = await get_thread()
    assistant = get_assistants()['SiriSelectorAssistant']

    for message in messages.messages:
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role=message.role,
            content=message.content
        )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run_status.status == 'completed':
            break

        elif run_status.status == 'requires_action':
            logging.info('Run requires action, a function is needed to continue the conversation.')

            tool_outputs = []
            for function_call in run_status.required_action.submit_tool_outputs.tool_calls:

                logging.info(f'Function call: {function_call}')
                if function_call.type == 'function':
                    result_data = await return_output_functions(
                        FunctionPayload(
                            thread_id=thread.id,
                            run_id=run.id,
                            function_name=function_call.function.name,
                            function_id=function_call.id,
                            function_params=json.loads(function_call.function.arguments)
                        )
                    )

                    tool_outputs.append(
                        {
                            "tool_call_id": function_call.id,
                            "output": result_data.output.get('message', 'No output for this function'),
                        }
                    )

            try:
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            except Exception as e:
                pass

    openai_response = client.beta.threads.messages.list(
        thread_id=thread.id,
        limit=10,
        order="desc"
    )

    data = openai_response.data[0].model_dump()

    try:
        content = json.loads(data['content'][0]['text']['value'].replace('```json', '').replace('```', ''))
    except json.JSONDecodeError:
        raise Exception('OpenAI response is not a valid JSON')

    question_pattern = r'[^.?!]*\?'

    questions = re.findall(question_pattern, content['message'])

    if len(questions) > 0:
        question = questions[0].strip()
        text_without_questions = re.sub(question_pattern, '', content['message']).strip()
        content['question'] = question
        content['message'] = text_without_questions
    else:
        content['question'] = ''
        content['message'] = content['message']

    return {
        'role': data['role'],
        'content': content,
        'created_at': datetime.utcfromtimestamp(data['created_at']).strftime('%Y-%m-%d %H:%M:%S'),
        'run_id': run.id,
        'thread_id': thread.id
    }
