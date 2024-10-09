import os
import io
from dotenv import load_dotenv
from aiogram import F, Router, types, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardButton, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from keyboards import keyboards as kb
from database import crud as rq
from keyboards import inline as in_kb
from services import service as ser
from services.supabase_storage import get_public_url
from keyboards import pagination_words as pagination
from services.voice_recognition import recognize_speech_from_voice
from services.openrouter_translation import translation
from services.sber_speech import get_speech
from services.yandex_image import get_image_id, retry_get_image


router_translation = Router()

load_dotenv()

bot = Bot(token=os.environ.get("BOT_TOKEN"))


@router_translation.message(F.text == 'Перевод')
async def show_lessons_command(message: Message):
    await message.answer('ВВеди слово')
    await message.delete()
