import json
import requests

from django.conf import settings

from loguru import logger


def format_text(text: str) -> str:
    """
    Преобразует ответ от YaGPT API в текстовый вид
    """
    response_dict: dict = json.loads(text)
    answer: str = response_dict['result']['alternatives'][0]['message']['text']
    if not answer.endswith('.') and not answer.endswith('?') and not answer.endswith('!'):
        answer += '...'
    return answer


URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
API_KEY: str = settings.YAGPT_API_KEY
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {API_KEY}"
}


def make_request(system_text: str, user_text: str, stream: bool = False, temperature: float = 0.3,
                 max_tokens: int = 100) -> str:
    prompt = {
        "modelUri": "gpt://b1ggjnuhu5mmhqqnag0t/yandexgpt/latest",
        "completionOptions": {
            "stream": stream,
            "temperature": temperature,
            "maxTokens": max_tokens
        },
        "messages": [
            {
                "role": "system",
                "text": system_text
            },
            {
                "role": "user",
                "text": user_text
            }
        ]
    }

    response = requests.post(URL, headers=HEADERS, json=prompt)
    temp_result = response.text
    if response.status_code != 200:
        final_answer = "Произошла ошибка :("
        logger.error(temp_result)
    else:
        final_answer = format_text(temp_result)

    return final_answer
