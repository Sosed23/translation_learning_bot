from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from database import crud as rq


def get_navigation_keyboard(current_index, total_items):
    buttons = []
    # Кнопка "Назад", если это не первый элемент
    if current_index > 0:
        buttons.append(InlineKeyboardButton(text="◀️ Назад",
                                            callback_data=f"prev_{current_index}"))
    # Кнопка "Вперед", если это не последний элемент
    if current_index < total_items - 1:
        buttons.append(InlineKeyboardButton(text="Вперед ▶️",
                                            callback_data=f"next_{current_index}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def show_paginated_item(message, items, current_index, state, edit=False):
    current_item = items[current_index]

    # Извлекаем данные текущего элемента
    title = current_item.title
    translation = current_item.translation
    transcription = current_item.transcription
    image_id_bot = current_item.image_id_bot
    audio_id_bot = current_item.audio_id_bot
    word_id = current_item.id
    lesson_id = current_item.lesson_id
    user_id = current_item.user_id

    await rq.create_history_views_word(word_id=word_id, lesson_id=lesson_id, user_id=user_id)

    history_view = await rq.get_history_views_by_lesson_and_word(word_id=word_id, lesson_id=lesson_id, user_id=user_id)

    if history_view is not None:
        count_history_view = len(history_view)
    else:
        count_history_view = 0

    # Формируем текст сообщения
    item_summary = (f"Текст: <strong>{title}</strong>\n"
                    f"Перевод: <strong>{translation}</strong>\n"
                    f"Транскрипция: <strong>[{transcription}]</strong>\n\n"
                    f'Количество повторений: 👁‍🗨 <strong>{count_history_view}</strong>'
                    )

    # Обновляем или отправляем новое фото
    if image_id_bot:
        media_photo = InputMediaPhoto(
            media=image_id_bot, caption=item_summary, parse_mode="HTML")
        if edit:
            try:
                await message.edit_media(media=media_photo, reply_markup=get_navigation_keyboard(current_index, len(items)))
            except Exception as e:
                await message.answer_photo(photo=image_id_bot, caption=item_summary, reply_markup=get_navigation_keyboard(current_index, len(items)), parse_mode="HTML")
        else:
            await message.answer_photo(photo=image_id_bot, caption=item_summary, reply_markup=get_navigation_keyboard(current_index, len(items)), parse_mode="HTML")

    # Обрабатываем аудио
    if audio_id_bot:
        # Получаем предыдущее сообщение с аудио из состояния
        data = await state.get_data()
        previous_audio_message_id = data.get('audio_message_id')

        # Удаляем предыдущее сообщение с аудио, если оно существует
        if previous_audio_message_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=previous_audio_message_id)
            except Exception as e:
                pass  # Игнорируем ошибку, если сообщение уже удалено или не найдено

        # Отправляем новое голосовое сообщение
        audio_message = await message.answer_voice(voice=audio_id_bot)

        # Сохраняем ID нового голосового сообщения в состоянии
        await state.update_data(audio_message_id=audio_message.message_id)

    # Если ни фото, ни аудио нет, обновляем текст
    if not image_id_bot and not audio_id_bot:
        if edit:
            await message.edit_text(item_summary, reply_markup=get_navigation_keyboard(current_index, len(items)), parse_mode="HTML")
        else:
            await message.answer(item_summary, reply_markup=get_navigation_keyboard(current_index, len(items)), parse_mode="HTML")


async def handle_previous(callback_query, state):
    data = await state.get_data()
    current_index = data['current_index']

    # Переход на предыдущий элемент
    new_index = current_index - 1
    await state.update_data(current_index=new_index)

    items = data['items']
    await show_paginated_item(callback_query.message, items, new_index, state=state, edit=True)
    await callback_query.answer()


async def handle_next(callback_query, state):
    data = await state.get_data()
    current_index = data['current_index']

    # Переход на следующий элемент
    new_index = current_index + 1
    await state.update_data(current_index=new_index)

    items = data['items']
    await show_paginated_item(callback_query.message, items, new_index, state=state, edit=True)
    await callback_query.answer()
