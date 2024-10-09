import requests
import sys
import base64
import time
from services.access.token_yandex_art import get_token_yandex

sys.stdout.reconfigure(encoding='utf-8')

iam_token = get_token_yandex()


def get_image_id(word: str):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": "art://b1g523ckrqpdiqtj019j/yandex-art/latest",
        "generationOptions": {
            "seed": "1863",
            "aspectRatio": {
                "widthRatio": "1",
                "heightRatio": "1"
            }
        },
        "messages": [
            {
                "weight": "1",
                "text": f"Основной объект рисунка должен быть {word}. Стиль должен быть как мультфильме. Рисунок должен воспринимать маленький ребенок."
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        operation_id = response_data.get('id')
        if operation_id:
            print(f"ID операции: {operation_id}")
            return operation_id
        else:
            print("ID не найден в ответе")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return None


def retry_get_image(operation_id: str, en_word: str, max_retries: int = 10, delay: int = 3):
    def wrapper():
        try:
            return get_image(operation_id, en_word)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return None

    for attempt in range(max_retries):
        result = wrapper()
        if result is not None:
            return result
        print(
            f"Попытка {attempt + 1} не удалась. Повтор через {delay} секунд...")
        time.sleep(delay)

    print(f"Не удалось получить изображение после {max_retries} попыток.")
    return None


def get_image(operation_id: str, en_word: str):
    url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
    headers = {
        'Authorization': f'Bearer {iam_token}'
    }

    max_retries = 5
    delay = 3

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            image_base64 = response_data.get('response', {}).get('image', '')
            if image_base64:
                image_data = base64.b64decode(image_base64)
                with open(f'storage/images/{en_word}.jpeg', 'wb') as file:
                    file.write(image_data)
                print(f"Изображение сохранено как {en_word}.jpeg")
                return image_data
            else:
                print("Изображение не найдено в ответе")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Попытка {attempt + 1} не удалась. Ошибка: {e}")
            if attempt < max_retries - 1:
                print(f"Повтор через {delay} секунд...")
                time.sleep(delay)
            else:
                print(
                    f"Не удалось получить изображение после {max_retries} попыток.")
                return None


def retry_get_image(operation_id: str, en_word: str, max_retries: int = 10, delay: int = 3):
    for attempt in range(max_retries):
        result = get_image(operation_id, en_word)
        if result is not None:
            return result
        print(
            f"Попытка {attempt + 1} не удалась. Повтор через {delay} секунд...")
        time.sleep(delay)

    print(f"Не удалось получить изображение после {max_retries} попыток.")
    return None
