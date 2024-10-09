# Используем официальный образ Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /code

# Устанавливаем системные зависимости, включая PortAudio
RUN apt-get update && apt-get install -y portaudio19-dev

# Копируем файл с зависимостями
COPY ./requirements.txt /code/requirements.txt

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r /code/requirements.txt

# Копируем все файлы проекта
COPY ./ /code/

# Команда для запуска бота
CMD ["python", "aiogram_bot/run.py"]
