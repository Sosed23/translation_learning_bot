from services.openrouter_translation import translation
from services.sber_speech import get_speech
from services.yandex_image import get_image_id, get_image
from services.supabase_storage import upload_image, get_public_url
import time
import requests


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


def transl_speech_art(word: str, content: str):
    try:
        en_word, transcription = translation(content=content)

        if en_word and transcription:
            print(f"Перевод слова: {en_word}")
            print(f"Транскрипция: {transcription}")
        else:
            print("Не удалось получить перевод или транскрипцию.")
            return None, None

        try:
            get_speech(en_word=en_word)
        except Exception as e:
            print(f"Ошибка при получении аудио: {e}")

        operation_id = get_image_id(word=word)

        if operation_id:
            image_data = retry_get_image(
                operation_id=operation_id, en_word=en_word)
            if image_data:
                print(f"Изображение успешно получено для слова: {en_word}")

            else:
                print(f"Не удалось получить изображение для слова: {en_word}")
        else:
            print("Не удалось получить ID операции для генерации изображения.")

        return en_word, transcription

    except Exception as e:
        print(f"Произошла ошибка в процессе обработки: {e}")
        return None, None
