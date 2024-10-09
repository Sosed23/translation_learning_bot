from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_navigation_keyboard(current_index: int, total_items: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для навигации по страницам (объектам).

    :param current_index: Текущий индекс объекта.
    :param total_items: Общее количество объектов.
    :return: InlineKeyboardMarkup с кнопками навигации.
    """
    buttons = []

    # Кнопка "Назад" появляется, если это не первый элемент
    if current_index > 0:
        buttons.append(InlineKeyboardButton(text="◀️ Назад",
                       callback_data=f"prev_{current_index}"))

    # Кнопка "Вперед" появляется, если это не последний элемент
    if current_index < total_items - 1:
        buttons.append(InlineKeyboardButton(text="Вперед ▶️",
                       callback_data=f"next_{current_index}"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons])


async def show_paginated_item(message, items, current_index, edit=False):
    """
    Отображает текущий элемент из списка с навигацией.

    :param message: Объект сообщения, в котором будет отображаться элемент.
    :param items: Список элементов для отображения.
    :param current_index: Текущий индекс отображаемого элемента.
    :param edit: Флаг, редактировать ли существующее сообщение или отправить новое.
    """
    item = items[current_index]

    # Формируем текст сообщения (это может быть урок, слово, любой другой объект)
    item_text = (f"Элемент {current_index + 1}/{len(items)}\n\n"
                 f"Название: {item.name}\n"
                 f"Описание: {item.description if item.description else 'Нет описания'}\n")

    if edit:
        await message.edit_text(item_text, reply_markup=get_navigation_keyboard(current_index, len(items)))
    else:
        await message.answer(item_text, reply_markup=get_navigation_keyboard(current_index, len(items)))


async def handle_previous(callback, state, items_key='items'):
    """
    Обрабатывает нажатие кнопки "Назад" в пагинаторе.

    :param callback: Объект CallbackQuery.
    :param state: FSMContext для хранения текущего состояния.
    :param items_key: Ключ для хранения списка элементов в состоянии.
    """
    data = await state.get_data()
    current_index = data['current_index']
    new_index = current_index - 1
    await state.update_data(current_index=new_index)

    items = data[items_key]
    await show_paginated_item(callback.message, items, new_index, edit=True)
    await callback.answer()


async def handle_next(callback, state, items_key='items'):
    """
    Обрабатывает нажатие кнопки "Вперед" в пагинаторе.

    :param callback: Объект CallbackQuery.
    :param state: FSMContext для хранения текущего состояния.
    :param items_key: Ключ для хранения списка элементов в состоянии.
    """
    data = await state.get_data()
    current_index = data['current_index']
    new_index = current_index + 1
    await state.update_data(current_index=new_index)

    items = data[items_key]
    await show_paginated_item(callback.message, items, new_index, edit=True)
    await callback.answer()
