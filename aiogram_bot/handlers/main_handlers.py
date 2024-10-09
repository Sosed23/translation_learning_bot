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


router = Router()

load_dotenv()

bot = Bot(token=os.environ.get("BOT_TOKEN"))


@router.message(CommandStart())
async def cmd_start(message: Message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    await rq.create_user(message.from_user.id, first_name, last_name)
    await message.answer('Добро пожаловать в приложения для изучения английского языка!', reply_markup=kb.main)


##################### ОТОБРАЗИТЬ СПИСОК УРОКОВ ############################

async def show_lessons(message: Message):
    # Получаем пользователя
    user = await rq.get_user_by_id(user_id=message.from_user.id)

    # Получаем список уроков для пользователя
    lessons = await rq.get_lessons_by_user(user_id=user.id)

    # Проверяем, есть ли уроки
    if not lessons:
        await message.answer('У вас пока нет уроков.')
        return

    # Создаем список кнопок с "Добавить урок" первой
    buttons = [
        [InlineKeyboardButton(
            text='Добавить новый урок', callback_data=f'add_lesson')]
    ] + [
        [InlineKeyboardButton(
            text=lesson.name, callback_data=f'lesson_{lesson.id}')]
        for lesson in lessons
    ]

    # Создаем инлайн-клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    # Отправляем сообщение с инлайн-клавиатурой
    await message.answer('Ваши уроки:', reply_markup=keyboard)


@router.message(F.text == 'Обучение')
async def show_lessons_command(message: Message):
    await show_lessons(message)
    await message.delete()

##################### ДОБАВИТЬ НОВЫЙ УРОК ############################


class Add_lesson(StatesGroup):
    name = State()


@router.callback_query(F.data == 'add_lesson')
async def add_lesson_start(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(Add_lesson.name)
    await callback_query.message.answer('Укажите название урока')
    await callback_query.answer()


@router.message(Add_lesson.name)
async def add_lesson(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()

    lesson_data = {
        "name": data.get("name")
    }

    user = await rq.get_user_by_id(user_id=message.from_user.id)

    await rq.create_lesson(name=lesson_data["name"], user_id=user.id)

    await message.answer(
        f'<strong>Добавлен новый урок:</strong>\n'
        f'{data["name"]}\n',
        parse_mode="HTML"
    )

    await state.clear()

    await show_lessons(message)


################ ОПИСАНИЕ УРОКА ####################

@router.callback_query(F.data.startswith('lesson_'))
async def handle_lesson_callback(callback_query: CallbackQuery, state: FSMContext):
    lesson_id = int(callback_query.data.split('_')[1])

    # Получаем информацию о выбранном уроке
    lesson = await rq.get_lesson_by_id(lesson_id)

    # Подсчитываем количество слов
    all_words_lesson = await rq.get_words_by_lesson(lesson_id=lesson_id)
    word_count = len(all_words_lesson)

    # Отправляем информацию о выбранном уроке
    await callback_query.message.answer(
        f'Вы выбрали урок: {lesson.name}\n'
        f"Количество слов в уроке: {word_count}",
        reply_markup=in_kb.get_callback_btns(
            btns={
                "Добавить слово": f"add-word_{lesson_id}",
                "Удалить урок": f"delete-lesson_{lesson_id}",
                "Повторить слова": f"repeat-word_{lesson_id}",
                "Голосовой перевод": f"learning-word_{lesson_id}",
                "Написать слова": f"make-word_{lesson_id}",
            },
            sizes=(2, 1, 2)
        )
    )
    await callback_query.answer()


# ПОВТОРИТЬ СЛОВА ############################ (!!!!!!!!!!!!!!!! ОШИБКА)

@router.callback_query(F.data.startswith('repeat-word_'))
async def handle_word_callback(callback_query: CallbackQuery, state: FSMContext):
    lesson_id = int(callback_query.data.split('_')[1])

    # Получаем список слов для урока
    all_words = await rq.get_words_by_lesson(lesson_id=lesson_id)

    if not all_words:
        await callback_query.message.answer("Нет слов для данного урока.")
        return

    # Сохраняем список слов и текущий индекс в состоянии
    await state.update_data(items=all_words, current_index=0)

    # Отображаем первое слово с навигацией
    await pagination.show_paginated_item(callback_query.message, all_words, current_index=0, state=state)

    # Подтверждаем обработку callback
    await callback_query.answer()


@router.callback_query(F.data.startswith('prev_'))
async def previous_word(callback_query: CallbackQuery, state: FSMContext):
    await pagination.handle_previous(callback_query, state)


@router.callback_query(F.data.startswith('next_'))
async def next_word(callback_query: CallbackQuery, state: FSMContext):
    await pagination.handle_next(callback_query, state)


##################### УДАЛИТЬ УРОК ############################

@router.callback_query(F.data.startswith('delete-lesson_'))
async def delete_lesson_callback(callback_query: CallbackQuery, state: FSMContext):
    lesson_id = int(callback_query.data.split('_')[1])

    # Удаляем урок
    await rq.delete_lesson(lesson_id=lesson_id)

    # Отправляем сообщение пользователю о том, что урок удалён
    await callback_query.message.answer('Урок успешно удалён.')

    # Получаем пользователя
    user_id = callback_query.from_user.id
    user = await rq.get_user_by_id(user_id=user_id)

    # Получаем список уроков для пользователя и отображаем его
    lessons = await rq.get_lessons_by_user(user_id=user.id)

    if not lessons:
        await callback_query.message.answer('У вас пока нет уроков.')
        return

    # Создаем список кнопок с "Добавить урок" первой
    buttons = [
        [InlineKeyboardButton(
            text='Добавить новый урок', callback_data=f'add_lesson')]
    ] + [
        [InlineKeyboardButton(
            text=lesson.name, callback_data=f'lesson_{lesson.id}')]
        for lesson in lessons
    ]

    # Создаем инлайн-клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    # Отправляем сообщение с инлайн-клавиатурой
    await callback_query.message.answer('Ваши уроки:', reply_markup=keyboard)

    await callback_query.answer()


##################### ДОБАВИТЬ СЛОВА ############################

class Add_word(StatesGroup):
    direction = State()
    name = State()


@router.callback_query(F.data.startswith('add-word_'))
async def add_word_callback(callback_query: CallbackQuery, state: FSMContext):
    lesson_id = int(callback_query.data.split('_')[1])
    await state.update_data(lesson_id=lesson_id)
    await show_direction_keyboard(callback_query.message, state)
    await callback_query.answer()


async def show_direction_keyboard(message: Message, state: FSMContext):

    all_direction_translations = await rq.get_all_direction_translation()

    buttons = []
    for direction_translation in all_direction_translations:
        button_text = f"{direction_translation.language_input.name} ➡️ {direction_translation.language_output.name}"
        callback_data = f'direction_{direction_translation.id}'
        buttons.append([InlineKeyboardButton(
            text=button_text, callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer('Выберете направление перевода', reply_markup=keyboard)
    await state.set_state(Add_word.direction)


@router.callback_query(F.data.startswith('direction_'))
async def add__direction(callback_query: CallbackQuery, state: FSMContext):

    direction_id = int(callback_query.data.split('_')[1])

    direction_data = await rq.get_direction_translation_by_id(direction_id=direction_id)

    await state.update_data(
        language_input_name=direction_data.language_input.name,
        language_output_name=direction_data.language_output.name,
        language_input_id=direction_data.language_input.id,
        language_output_id=direction_data.language_output.id
    )

    await callback_query.message.answer(
        f"Вы выбрали направление: {direction_data.language_input.name} -> {direction_data.language_output.name}"
    )

    await state.set_state(Add_word.name)
    await callback_query.message.answer('Напишите слово')
    await callback_query.answer()


@router.message(Add_word.name)
async def add_prod_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.lower())

    data = await state.get_data()
    lesson_id = data.get('lesson_id')
    user_id = await rq.get_user_by_id(user_id=message.from_user.id)

    language_input_id = data.get('language_input_id')
    language_input_name = data.get('language_input_name')
    language_output_name = data.get('language_output_name')

    word = f'{data["name"]}'

    await message.answer(
        f'Новое слово в процесс добавления: <strong>{data["name"]}</strong>',
        parse_mode="HTML"
    )

    if language_input_id == 1:

        ################ TRANSLATION RU ###########################

        content_word_ru = (f"Переведи '{word}' на {language_output_name} язык и напиши транскрипцию переведенного слова без добавления квадратных скобок. "
                           f"Ответ нужно оформить в json формате с ключами translation и transcription")

        en_word, transcription = translation(
            content=content_word_ru)

        ############### SPEECH FOR LISTEN #####################

        get_speech(en_word=en_word)

        audio_path = f'storage/audios/{en_word}.opus'
        audio = FSInputFile(audio_path)
        # sent_audio_message = await message.answer_audio(audio=audio)
        # audio_file_id = sent_audio_message.voice.file_id

        ############### GET IMAGE #####################

        if en_word:

            operation_id = get_image_id(word=word)

            image_data = retry_get_image(
                operation_id=operation_id, en_word=en_word)
            if image_data:
                print(f"Изображение успешно получено для слова: {en_word}")

            else:
                print(f"Не удалось получить изображение для слова: {en_word}")

            image_path = f'storage/images/{en_word}.jpeg'
            photo = FSInputFile(image_path)
            sent_photo_message = await message.answer_photo(
                photo=photo,
                caption=f'Введенный текст: <strong>{word}</strong>\n'
                        f'Перевод текста: <strong>{en_word}</strong>\n'
                        f'Транскрипция: <strong>[{transcription}]</strong>\n',
                parse_mode="HTML"
            )

            photo_file_id = sent_photo_message.photo[-1].file_id

            sent_audio_message = await message.answer_audio(audio=audio)
            audio_file_id = sent_audio_message.voice.file_id

            # Создаем запись в БД, если аудио отправлено
            create_word_db = await rq.create_word(
                title=word,
                translation=en_word,
                transcription=transcription,
                image_id_bot=photo_file_id,
                audio_id_bot=audio_file_id,
                language_id=2,
                lesson_id=lesson_id,
                user_id=user_id.id,
            )

    else:

        ################ TRANSLATION NOT RU ###########################

        content_word_not_ru = (f"Переведи '{word}' на {language_input_name} язык и напиши транскрипцию для '{word}' "
                               f"без добавления квадратных скобок, "
                               f"Ответ нужно оформить в json формате с ключами translation и transcription")

        en_word, transcription = translation(
            content=content_word_not_ru)

        ############### SPEECH FOR LISTEN #####################

        get_speech(en_word=word)

        audio_path = f'storage/audios/{word}.opus'
        audio = FSInputFile(audio_path)
        # sent_audio_message = await message.answer_audio(audio=audio)
        # audio_file_id = sent_audio_message.voice.file_id

        ############### GET IMAGE #####################

        if en_word:

            operation_id = get_image_id(word=en_word)

            image_data = retry_get_image(
                operation_id=operation_id, en_word=word)
            if image_data:
                print(f"Изображение успешно получено для слова: {word}")

            else:
                print(f"Не удалось получить изображение для слова: {word}")

            image_path = f'storage/images/{word}.jpeg'
            photo = FSInputFile(image_path)
            sent_photo_message = await message.answer_photo(
                photo=photo,
                caption=f'Введенный текст: {word}\n'
                        f'Перевод текста: {en_word}\n'
                        f'Транскрипция: [{transcription}]\n'
            )

            photo_file_id = sent_photo_message.photo[-1].file_id

            sent_audio_message = await message.answer_audio(audio=audio)
            audio_file_id = sent_audio_message.voice.file_id

            # Создаем запись в БД, если аудио отправлено
            create_word_db = await rq.create_word(
                title=en_word,
                translation=word,
                transcription=transcription,
                image_id_bot=photo_file_id,
                audio_id_bot=audio_file_id,
                language_id=2,
                lesson_id=lesson_id,
                user_id=user_id.id,
            )

    await state.clear()
