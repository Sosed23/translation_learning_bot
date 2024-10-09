from aiogram.types import InputMediaPhoto
from database import crud as rq
# Функция отображения элемента без использования инлайн-кнопок


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

    history_learning_word = await rq.get_history_learning_by_word_id(word_id=word_id)

    if history_learning_word is not None:
        count_repeat_word = len(history_learning_word)
    else:
        count_repeat_word = 0

    # Суммируем значения поля "rating", где rating == 1
    total_rating_plus = 0
    for item in history_learning_word:
        if item.rating == 1:
            total_rating_plus += 1

    # Суммируем значения поля "rating", где rating == 1
    total_rating_minus = 0
    for item in history_learning_word:
        if item.rating == 0:
            total_rating_minus += 1

    # Формируем текст сообщения
    item_summary = (
        f"Текст: <strong>{translation}</strong>\n"
        f"Транскрипция: <strong>{transcription}</strong>\n\n"
        f'Голосовой перевод: 👁‍🗨 {count_repeat_word} | 👍 {total_rating_plus} | 👎 {total_rating_minus}\n')

    # Обновляем или отправляем новое фото
    if image_id_bot:
        media_photo = InputMediaPhoto(media=image_id_bot, caption=item_summary)
        if edit:
            try:
                await message.edit_media(media=media_photo, parse_mode="HTML")
            except Exception:
                await message.answer_photo(photo=image_id_bot, caption=item_summary, parse_mode="HTML")
        else:
            await message.answer_photo(photo=image_id_bot, caption=item_summary, parse_mode="HTML")

    # Обрабатываем аудио
    if audio_id_bot:
        # Получаем предыдущее сообщение с аудио из состояния
        data = await state.get_data()
        previous_audio_message_id = data.get('audio_message_id')

        # Удаляем предыдущее сообщение с аудио, если оно существует
        if previous_audio_message_id:
            try:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=previous_audio_message_id)
            except Exception:
                pass  # Игнорируем ошибку, если сообщение уже удалено или не найдено

        # Отправляем новое голосовое сообщение
        audio_message = await message.answer_voice(voice=audio_id_bot)

        # Сохраняем ID нового голосового сообщения в состоянии
        await state.update_data(audio_message_id=audio_message.message_id)

    # Если ни фото, ни аудио нет, обновляем текст
    if not image_id_bot and not audio_id_bot:
        if edit:
            await message.edit_text(item_summary, parse_mode="HTML")
        else:
            await message.answer(item_summary, parse_mode="HTML")
