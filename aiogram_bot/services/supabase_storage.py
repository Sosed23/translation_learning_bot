from supabase import create_client, Client
from dotenv import load_dotenv
import os
import sys


load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Инициализация клиента Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def upload_image(file_path: str, bucket_name: str, file_name: str):
    # Открытие файла изображения в бинарном режиме
    with open(file_path, "rb") as file:
        # Опции загрузки файла, включая указание MIME-типа
        # Укажите MIME-тип изображения
        file_options = {"content-type": "image/jpeg"}

        # Загрузка файла в указанный бакет
        response = supabase.storage.from_(
            bucket_name).upload(file_name, file, file_options)

        # Проверка ответа на успешность
        if response.status_code == 200:
            print("Файл успешно загружен:", response.json())
            # Получение URL загруженного файла
            file_url = get_public_url(bucket_name, file_name)
            print("URL файла:", file_url)
        else:
            print("Ошибка при загрузке:", response.json())


def get_public_url(bucket_name: str, file_name: str) -> str:
    # Получение публичного URL файла
    return supabase.storage.from_(bucket_name).get_public_url(file_name)


# # Путь к файлу изображения, имя бакета и имя файла в Supabase
# file_path = "image1.jpeg"  # Укажите путь к вашему изображению
# bucket_name = "English"    # Укажите имя вашего бакета
# file_name = "uploaded-image8.jpeg"  # Укажите имя для сохранения файла в бакете

# # Вызов функции загрузки
# upload_image(file_path, bucket_name, file_name)
