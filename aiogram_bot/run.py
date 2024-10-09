from dotenv import load_dotenv
from handlers.main_handlers import router
from handlers.assessment_voice import router_assessment_voice
from handlers.translation import router_translation
from aiogram import Bot, Dispatcher
from database.db import create_db, drop_db
import asyncio
import os


load_dotenv()


bot = Bot(token=os.environ.get("BOT_TOKEN"))
dp = Dispatcher()


dp.include_router(router)
dp.include_router(router_assessment_voice)
dp.include_router(router_translation)


async def main():

    # await drop_db()
    await create_db()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=['*'])

if __name__ == "__main__":
    asyncio.run(main())
