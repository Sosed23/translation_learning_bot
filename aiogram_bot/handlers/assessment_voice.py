import io
import os
from dotenv import load_dotenv
from aiogram import F, Router, types, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardButton, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from keyboards import keyboards as kb
import database.crud as rq
from keyboards import inline as in_kb
from services import service as ser
from services.supabase_storage import get_public_url
from keyboards import pagination_translation_text as pagination
from services.voice_recognition import recognize_speech_from_voice


router_assessment_voice = Router()

load_dotenv()

bot = Bot(token=os.environ.get("BOT_TOKEN"))


class VoiceRecognitionState(StatesGroup):
    waiting_for_voice = State()


@router_assessment_voice.message(VoiceRecognitionState.waiting_for_voice, F.voice)
async def handle_voice_message(message: Message, state: FSMContext):
    voice = message.voice  # Доступ к объекту Voice
    voice_file_id = voice.file_id  # Получаем file_id для загрузки файла

    # Скачиваем голосовой файл
    voice_file = await bot.download(voice_file_id)

    # Сохраняем голосовое сообщение временно как файл
    audio_data = io.BytesIO()
    audio_data.write(voice_file.read())
    audio_data.seek(0)

    # Передаём файл в функцию для распознавания
    recognized_text = recognize_speech_from_voice(audio_data)

    # Получаем текущее слово из состояния
    data = await state.get_data()
    current_item = data.get("current_item")
    if not current_item:
        await message.answer("Произошла ошибка. Текущее слово не найдено.")
        return

    # Предполагаем, что current_item — это объект класса Word с атрибутом 'title'
    original_word = current_item.title
    word_id = current_item.id
    lesson_id = data.get("lesson_id")
    user = user = await rq.get_user_by_id(user_id=message.from_user.id)

    # Сравниваем распознанный текст с текущим словом
    if recognized_text.strip().lower() == original_word.strip().lower():
        await message.answer(f"Правильно! Слово: {original_word}")
        await rq.create_history_learning(voice_text=recognized_text,
                                         audio_id_bot=voice_file_id,
                                         rating=1,
                                         method_learning_id=1,
                                         word_id=word_id,
                                         lesson_id=lesson_id,
                                         user_id=user.id
                                         )

        # await message.answer(f"{history_learning}")
    else:
        await message.answer(f"Неправильно. Ожидалось: {original_word}, а вы сказали: {recognized_text}")
        await rq.create_history_learning(voice_text=recognized_text,
                                         audio_id_bot=voice_file_id,
                                         rating=0,
                                         method_learning_id=1,
                                         word_id=word_id,
                                         lesson_id=lesson_id,
                                         user_id=user.id
                                         )

    # Переходим к следующему слову или завершаем урок
    items = data.get("items")
    current_index = data.get("current_index", 0)

    if current_index + 1 < len(items):
        new_index = current_index + 1
        await state.update_data(current_index=new_index)
        await pagination.show_paginated_item(message, items, new_index, state=state)

        # Обновляем текущее слово в состоянии
        new_item = items[new_index]
        await state.update_data(current_item=new_item)

        await message.answer("Теперь отправьте новое голосовое сообщение для распознавания.")
    else:
        await message.answer("Урок завершён.")
        await state.clear()


@router_assessment_voice.callback_query(F.data.startswith('learning-word_'))
async def learning_word_callback(callback_query: CallbackQuery, state: FSMContext):
    lesson_id = int(callback_query.data.split('_')[1])

    # Получаем список слов для урока
    all_words = await rq.get_words_by_lesson(lesson_id=lesson_id)

    await state.update_data(lesson_id=lesson_id)

    if not all_words:
        await callback_query.message.answer("Нет слов для данного урока.")
        return

    # Сохраняем список слов и текущий индекс в состоянии
    await state.update_data(items=all_words, current_index=0)

    # Сохраняем текущее слово в состоянии для привязки
    current_item = all_words[0]
    await state.update_data(current_item=current_item)

    # Отображаем первое слово с навигацией
    await pagination.show_paginated_item(callback_query.message, all_words, current_index=0, state=state)

    # Переводим бота в состояние ожидания голосового сообщения
    await callback_query.message.answer("Теперь отправьте голосовое сообщение для распознавания.")
    await state.set_state(VoiceRecognitionState.waiting_for_voice)

    # Подтверждаем обработку callback
    await callback_query.answer()
