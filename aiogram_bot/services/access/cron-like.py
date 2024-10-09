# # pip install schedule

# import schedule
# import time

# # Функция для обновления токена
# def update_token():
#     # Логика получения нового токена
#     token = get_new_token()
#     # Логика сохранения токена, например, в файл или базу данных
#     save_token(token)
#     print("Токен обновлен!")

# # Функция для получения нового токена (пример)
# def get_new_token():
#     # Здесь будет запрос на сервер для получения нового токена
#     return "new_token_123"

# # Функция для сохранения токена (пример)
# def save_token(token):
#     # Сохранение токена, например, в файл
#     with open("token.txt", "w") as file:
#         file.write(token)

# # Запускаем обновление токена каждые 10 минут
# schedule.every(10).minutes.do(update_token)

# # Запускаем цикл, который постоянно проверяет расписание
# while True:
#     schedule.run_pending()
#     time.sleep(1)


# # pip install apscheduler
# # Пример использования APScheduler для запуска задачи каждый день в 6 утра:

# from apscheduler.schedulers.blocking import BlockingScheduler

# def job():
#     print("Job executed!")

# scheduler = BlockingScheduler()
# scheduler.add_job(job, 'cron', hour=6)
# scheduler.start()
