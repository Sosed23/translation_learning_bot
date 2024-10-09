import json
import sys
import requests
from datetime import datetime, timedelta
import jwt
import os

# Установка кодировки UTF-8 для консоли
sys.stdout.reconfigure(encoding='utf-8')

private_key_file = os.path.join(os.path.dirname(
    __file__), "private_key_yandex_art.json")


def get_token_yandex(private_key_file=private_key_file):

    try:
        # Чтение приватного ключа и идентификатора ключа (kid)
        with open(private_key_file, 'r') as key_file:
            key_data = json.load(key_file)
            private_key = key_data['private_key']  # Приватный ключ
            kid = key_data['id']  # Идентификатор ключа (key ID)
            # Идентификатор сервисного аккаунта
            service_account_id = key_data['service_account_id']

        # Создание JWT-токена
        now = datetime.utcnow()
        # Время жизни токена 10 минут
        expiration_time = now + timedelta(minutes=10)

        # Формирование JWT токена с использованием алгоритма PS256 и добавлением поля kid в заголовок
        jwt_token = jwt.encode(
            {
                'iat': now,
                'exp': expiration_time,
                'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
                'iss': service_account_id  # Идентификатор сервисного аккаунта
            },
            private_key,
            algorithm='PS256',
            headers={'kid': kid}  # Добавляем идентификатор ключа в заголовок
        )

        # Запрос IAM-токена
        response = requests.post(
            'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            json={'jwt': jwt_token}
        )

        # Обработка ответа
        if response.status_code == 200:
            iam_token_info = response.json()
            return iam_token_info['iamToken']
        else:
            print(
                f"Ошибка при получении IAM токена: {response.status_code}, {response.content}")
            return None
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return None


# Пример использования функции
iam_token = get_token_yandex()

if iam_token:
    print("IAM Token:", iam_token)
else:
    print("Не удалось получить IAM токен")
