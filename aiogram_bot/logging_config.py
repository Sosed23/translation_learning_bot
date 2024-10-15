from loguru import logger
import sys
import os

LOG_PATH = os.path.join(os.path.dirname(__file__),
                        "logs")  # Директория для логов
# Создаем директорию, если она не существует
os.makedirs(LOG_PATH, exist_ok=True)

# Получаем уровень логирования из переменной окружения
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logger.remove()
logger.add("app.log", format="{time} {level} {message}", level=LOG_LEVEL)


# logger.remove()  # Удаляем стандартный логгер, если он был
# # Логи в консоль
# logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
# logger.add(os.path.join(LOG_PATH, "app.log"), format="{time} {level} {message}",
#            level="INFO", rotation="10 MB", compression="zip")  # Логи в файл с ротацией
# logger.add(os.path.join(LOG_PATH, "errors.log"), format="{time} {level} {message}",
#            level="ERROR", rotation="10 MB", compression="zip")  # Ошибки в отдельный файл
