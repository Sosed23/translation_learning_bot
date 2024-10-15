import requests
import uuid
import sys
import os
import time
import json
from dotenv import load_dotenv
from threading import Thread
from datetime import datetime, timedelta
from aiogram_bot.logging_config import logger

# Загружаем переменные окружения
load_dotenv()

API_KEY_SBER = os.environ.get("API_KEY_SBER")

# Установка кодировки UTF-8 для консоли
sys.stdout.reconfigure(encoding='utf-8')

# Настройка логирования в файл
# logger.add("token_refresh_log.log",
#            format="{time} {level} {message}", level="INFO", rotation="1 week", compression="zip")

# URL для получения токена
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

headers = {
    "Authorization": f"Basic {API_KEY_SBER}==",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "scope": "SALUTE_SPEECH_PERS"
}

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token_sber_speech.json")


def save_token_to_file(token, expiration_time):
    """Сохраняет токен и время истечения в файл"""
    with open(TOKEN_FILE, "w") as file:
        json.dump({"access_token": token, "expires_at": expiration_time}, file)


def load_token_from_file():
    """Загружает токен из файла, если он существует и не истёк"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            data = json.load(file)
            if data.get("expires_at") > time.time():
                return data.get("access_token")
            else:
                logger.info("Токен истёк.")
    return None


def get_new_token():
    """Получение нового токена"""
    generated_uuid = str(uuid.uuid4())
    headers["RqUID"] = generated_uuid

    try:
        response = requests.post(url, headers=headers, data=data, verify=False)

        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get('access_token')
            expires_in = response_data.get('expires_in', 1800)

            if access_token:
                expiration_time = time.time() + expires_in
                save_token_to_file(access_token, expiration_time)
                logger.info(
                    f"Новый токен получен. Срок действия: {datetime.fromtimestamp(expiration_time)}")
                return access_token
            else:
                logger.error("Токен не найден в ответе")
        else:
            logger.error(
                f"Ошибка получения токена: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")

    return None


def get_access_token():
    """Проверка токена: загружает из файла или запрашивает новый"""
    token = load_token_from_file()
    if token:
        return token
    else:
        return get_new_token()


def token_refresh_task():
    """Задача для периодического обновления токена"""
    while True:
        token = load_token_from_file()
        if token is None or time.time() > json.load(open(TOKEN_FILE))['expires_at'] - 300:
            new_token = get_new_token()
            if new_token:
                logger.info(f"Токен успешно обновлен: {new_token[:10]}...")
            else:
                logger.error("Не удалось обновить токен.")
        time.sleep(60)


# Запуск задачи обновления токена в отдельном потоке
refresh_thread = Thread(target=token_refresh_task, daemon=True)
refresh_thread.start()

# Пример использования
if __name__ == "__main__":
    logger.info(
        "Скрипт запущен. Токен будет автоматически обновляться каждые 30 минут.")
    while True:
        access_token = get_access_token()
        if access_token:
            logger.info(f"Текущий токен: {access_token[:10]}...")
        else:
            logger.error("Не удалось получить токен.")
        time.sleep(300)
