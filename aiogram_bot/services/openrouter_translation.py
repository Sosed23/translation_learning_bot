import requests
import json
import sys
import os
from dotenv import load_dotenv


load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

sys.stdout.reconfigure(encoding='utf-8')


def translation(content: str = None):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        data=json.dumps({
            "model": "openai/gpt-3.5-turbo",  # mattshumer/reflection-70b:free
            "messages": [
                {"role": "user", "content": f"{content}"}
            ]

        })
    )

    print(content)

    # Проверка успешного ответа
    if response.status_code == 200:
        # Попробуем вывести ответ как JSON
        try:
            # Преобразуем ответ в JSON
            response_json = response.json()
            print(response_json)
            # Получаем содержимое поля 'content' из первого элемента 'choices'
            content = response_json['choices'][0]['message']['content']

            # Преобразуем строку JSON (которая находится в 'content') в словарь
            content_json = json.loads(content)

            # Извлекаем перевод (translation) и транскрипцию (transcription)
            en_word = content_json.get('translation')
            transcription = content_json.get('transcription')

            print(f"{en_word} [{transcription}]")

            return en_word, transcription
        except ValueError:
            print(response.text)
    else:
        print(f"Ошибка: {response.status_code}")

    return None, None  # Возвращаем None для обоих значений в случае ошибки


# translation(word='таракан')
