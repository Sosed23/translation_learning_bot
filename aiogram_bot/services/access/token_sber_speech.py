import requests
import time
import os
import json
from dotenv import load_dotenv
from logging_config import logger

# Загружаем переменные окружения
load_dotenv()

API_KEY_SBER = os.environ.get("API_KEY_SBER")

# URL для получения токена
TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token_sber_speech.json")


def save_token_to_file(token, expires_in):
    """Сохраняет токен в файл с указанием времени истечения."""
    expiration_time = time.time() + expires_in
    with open(TOKEN_FILE, "w") as file:
        json.dump({"access_token": token, "expires_at": expiration_time}, file)
    logger.info(
        f"Токен сохранен в файл. Действителен до: {time.ctime(expiration_time)}")


def load_token_from_file():
    """Загружает токен из файла, если он существует и не истек."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            data = json.load(file)
            if data["expires_at"] > time.time():
                logger.info(
                    f"Токен загружен из файла. Действителен до: {time.ctime(data['expires_at'])}")
                return data["access_token"]
            else:
                logger.info("Токен истек.")
    else:
        logger.info("Файл с токеном не найден.")
    return None


def get_new_token():
    """Запрашивает новый токен у API Sber."""
    headers = {
        "Authorization": f"Basic {API_KEY_SBER}==",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"scope": "SALUTE_SPEECH_PERS"}

    try:
        response = requests.post(
            TOKEN_URL, headers=headers, data=data, verify=False)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 1800)
            save_token_to_file(access_token, expires_in)
            logger.info("Новый токен успешно получен и сохранен.")
            return access_token
        else:
            logger.error(
                f"Ошибка получения токена: {response.status_code}, {response.text}")
    except Exception as e:
        logger.error(f"Ошибка при запросе нового токена: {e}")
    return None


def get_access_token():
    """Возвращает токен из файла или запрашивает новый, если он истек."""
    token = load_token_from_file()
    if token:
        return token
    else:
        logger.info(
            "Получаем новый токен, так как текущий отсутствует или истек.")
        return get_new_token()
