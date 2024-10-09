import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
from database.models import User, Lesson, Language, Word, History_learning, Method_learning, History_views_word, Direction_translation
from database.db import async_session_maker  # Импорт фабрики сессий


# === User CRUD ===

async def create_user(user_id: int, first_name: str = None, last_name: str = None, phone: str = None):
    """Создать нового пользователя, если он не существует."""
    async with async_session_maker() as session:
        # Проверка на существование пользователя
        existing_user = await session.execute(select(User).filter_by(user_id=user_id))
        if existing_user.scalar() is not None:
            return None  # Пользователь уже существует

        # Создание нового пользователя
        db_user = User(user_id=user_id, first_name=first_name,
                       last_name=last_name, phone=phone)
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user


async def get_user_by_id(user_id: int):
    """Получить пользователя по его user_id."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(User).filter(User.user_id == user_id))
        return result.scalars().first()


async def get_all_users():
    """Получить список всех пользователей."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(User))
        return result.scalars().all()


async def update_user(user_id: int, first_name: str = None, last_name: str = None, phone: str = None):
    """Обновить информацию о пользователе."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(User).filter(User.user_id == user_id))
        db_user = result.scalars().first()
        if not db_user:
            raise NoResultFound(f"User with id {user_id} not found")

        if first_name:
            db_user.first_name = first_name
        if last_name:
            db_user.last_name = last_name
        if phone:
            db_user.phone = phone

        await session.commit()
        await session.refresh(db_user)
        return db_user


async def delete_user(user_id: int):
    """Удалить пользователя по его user_id."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(User).filter(User.user_id == user_id))
        db_user = result.scalars().first()
        if db_user:
            await session.delete(db_user)
            await session.commit()
        return db_user


# === Lesson CRUD ===

async def create_lesson(name: str, user_id: int, description: str = None):
    """Создать урок для пользователя."""
    async with async_session_maker() as session:  # Открываем сессию
        db_lesson = Lesson(name=name, description=description, user_id=user_id)
        session.add(db_lesson)
        await session.commit()
        await session.refresh(db_lesson)
        return db_lesson


async def get_lessons_by_user(user_id: int):
    """Получить все уроки для определенного пользователя."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Lesson).filter(Lesson.user_id == user_id))
        return result.scalars().all()


async def get_lesson_by_id(lesson_id: int):
    """Получить урок по его lesson_id."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Lesson).filter(Lesson.id == lesson_id))
        return result.scalars().first()


async def update_lesson(lesson_id: int, name: str = None, description: str = None):
    """Обновить информацию о уроке."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Lesson).filter(Lesson.id == lesson_id))
        db_lesson = result.scalars().first()
        if not db_lesson:
            raise NoResultFound(f"Lesson with id {lesson_id} not found")

        if name:
            db_lesson.name = name
        if description:
            db_lesson.description = description

        await session.commit()
        await session.refresh(db_lesson)
        return db_lesson


async def delete_lesson(lesson_id: int):
    """Удалить урок по его id."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Lesson).filter(Lesson.id == lesson_id))
        db_lesson = result.scalars().first()
        if db_lesson:
            await session.delete(db_lesson)
            await session.commit()
        return db_lesson


# === Language CRUD ===

async def create_language(name: str):
    """Создать новый язык."""
    async with async_session_maker() as session:  # Открываем сессию
        db_language = Language(name=name)
        session.add(db_language)
        await session.commit()
        await session.refresh(db_language)
        return db_language


async def get_all_languages():
    """Получить список всех языков."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Language))
        return result.scalars().all()


async def update_language(language_id: int, name: str):
    """Обновить язык."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Language).filter(Language.id == language_id))
        db_language = result.scalars().first()
        if not db_language:
            raise NoResultFound(f"Language with id {language_id} not found")

        db_language.name = name

        await session.commit()
        await session.refresh(db_language)
        return db_language


async def delete_language(language_id: int):
    """Удалить язык по его id."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Language).filter(Language.id == language_id))
        db_language = result.scalars().first()
        if db_language:
            await session.delete(db_language)
            await session.commit()
        return db_language

# === Word CRUD ===


async def create_word(title: str, translation: str, transcription: str, image_id_bot: str = None,
                      audio_id_bot: str = None, language_id: int = None, lesson_id: int = None, user_id: int = None):
    """Создать новое слово."""
    async with async_session_maker() as session:  # Открываем сессию
        db_word = Word(
            title=title,
            translation=translation,
            transcription=transcription,
            image_id_bot=image_id_bot,
            audio_id_bot=audio_id_bot,
            language_id=language_id,
            lesson_id=lesson_id,
            user_id=user_id
        )
        session.add(db_word)
        await session.commit()
        await session.refresh(db_word)
        return db_word


async def get_words_by_lesson(lesson_id: int):
    """Получить все слова для определенного урока."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Word).filter(Word.lesson_id == lesson_id))
        return result.scalars().all()


async def update_word(word_id: int, title: str = None, translation: str = None, transcription: str = None,
                      image_id_bot: str = None, audio_id_bot: str = None):
    """Обновить информацию о слове."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Word).filter(Word.id == word_id))
        db_word = result.scalars().first()
        if not db_word:
            raise NoResultFound(f"Word with id {word_id} not found")

        if title:
            db_word.title = title
        if translation:
            db_word.translation = translation
        if transcription:
            db_word.transcription = transcription
        if image_id_bot:
            db_word.image_id_bot = image_id_bot
        if audio_id_bot:
            db_word.audio_id_bot = audio_id_bot

        await session.commit()
        await session.refresh(db_word)
        return db_word


async def delete_word(word_id: int):
    """Удалить слово по его id."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Word).filter(Word.id == word_id))
        db_word = result.scalars().first()
        if db_word:
            await session.delete(db_word)
            await session.commit()
        return db_word


# === History Learning CRUD https://t.me/PythonPathMaster/121===

# Создание новой записи
async def create_history_learning(voice_text: str = None, rating: int = None, audio_id_bot: str = None,
                                  method_learning_id: int = None, word_id: int = None,
                                  lesson_id: int = None, user_id: int = None):
    """Создать новую запись в истории обучения."""
    async with async_session_maker() as session:  # Открываем сессию
        db_history_learning = History_learning(
            voice_text=voice_text,
            audio_id_bot=audio_id_bot,
            rating=rating,
            method_learning_id=method_learning_id,
            word_id=word_id,
            lesson_id=lesson_id,
            user_id=user_id
        )
        session.add(db_history_learning)
        await session.commit()
        await session.refresh(db_history_learning)
        return db_history_learning


# Получение всех записей
async def get_all_history_learnings():
    """Получить все записи истории обучения."""
    async with async_session_maker() as session:
        result = await session.execute(select(History_learning))
        return result.scalars().all()


# Получение записи по условию (по ID)
async def get_history_learning_by_id(history_learning_id: int):
    """Получить запись истории обучения по её id."""
    async with async_session_maker() as session:
        result = await session.execute(select(History_learning).filter(History_learning.id == history_learning_id))
        db_history_learning = result.scalars().first()
        if db_history_learning:
            return {
                "id": db_history_learning.id,
                "voice_text": db_history_learning.voice_text,
                "audio_id_bot": db_history_learning.audio_id_bot,
                "rating": db_history_learning.rating,  # Добавляем рейтинг
                "method_learning_id": db_history_learning.method_learning_id,
                "word_id": db_history_learning.word_id,
                "lesson_id": db_history_learning.lesson_id,
                "user_id": db_history_learning.user_id
            }
        return None


# Получение записи по условию (по Word ID)
async def get_history_learning_by_word_id(word_id: int):
    """Получить запись истории обучения по её id."""
    async with async_session_maker() as session:
        result = await session.execute(select(History_learning).filter(History_learning.word_id == word_id))
        return result.scalars().all()


# Изменение записи по ID
async def update_history_learning(history_learning_id: int, voice_text: str = None, audio_id_bot: str = None,
                                  rating: int = None, method_learning_id: int = None, word_id: int = None,
                                  lesson_id: int = None, user_id: int = None):
    """Обновить информацию в записи истории обучения."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(History_learning).filter(History_learning.id == history_learning_id))
        db_history_learning = result.scalars().first()
        if not db_history_learning:
            raise NoResultFound(
                f"History learning record with id {history_learning_id} not found")

        if voice_text:
            db_history_learning.voice_text = voice_text
        if audio_id_bot:
            db_history_learning.audio_id_bot = audio_id_bot
        if rating is not None:
            db_history_learning.rating = rating  # Добавляем обновление рейтинга
        if method_learning_id:
            db_history_learning.method_learning_id = method_learning_id
        if word_id:
            db_history_learning.word_id = word_id
        if lesson_id:
            db_history_learning.lesson_id = lesson_id
        if user_id:
            db_history_learning.user_id = user_id

        await session.commit()
        await session.refresh(db_history_learning)
        return db_history_learning


# Удаление записи по ID
async def delete_history_learning(history_learning_id: int):
    """Удалить запись истории обучения по её id."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(History_learning).filter(History_learning.id == history_learning_id))
        db_history_learning = result.scalars().first()
        if db_history_learning:
            await session.delete(db_history_learning)
            await session.commit()
        return db_history_learning


# Получение записей с условием
async def get_filtered_history_learnings(condition):
    """Получить записи истории обучения по условию."""
    async with async_session_maker() as session:
        result = await session.execute(select(History_learning).filter(condition))
        return result.scalars().all()


# Получение записей с сортировкой
async def get_sorted_history_learnings(order_by_column):
    """Получить записи истории обучения с сортировкой по указанному полю."""
    async with async_session_maker() as session:
        result = await session.execute(select(History_learning).order_by(order_by_column))
        return result.scalars().all()


# Ограничение количества записей
async def get_limited_history_learnings(limit: int):
    """Получить ограниченное количество записей истории обучения."""
    async with async_session_maker() as session:
        result = await session.execute(select(History_learning).limit(limit))
        return result.scalars().all()


# # Обновление нескольких записей по условию
# async def update_multiple_history_learnings(condition, update_data: dict):
#     """Обновить несколько записей истории обучения по условию."""
#     async with async_session_maker() as session:
#         await session.execute(
#             update(History_learning).where(condition).values(update_data)
#         )
#         await session.commit()


# # Удаление нескольких записей по условию
# async def delete_multiple_history_learnings(condition):
#     """Удалить несколько записей истории обучения по условию."""
#     async with async_session_maker() as session:
#         await session.execute(delete(History_learning).where(condition))
#         await session.commit()


# # === History Learning CRUD ===

# async def create_history_learning(voice_text: str = None, audio_id_bot: str = None,
#                                   method_learning_id: int = None, word_id: int = None,
#                                   lesson_id: int = None, user_id: int = None):
#     """Создать новую запись в истории обучения."""
#     async with async_session_maker() as session:  # Открываем сессию
#         db_history_learning = History_learning(
#             voice_text=voice_text,
#             audio_id_bot=audio_id_bot,
#             method_learning_id=method_learning_id,
#             word_id=word_id,
#             lesson_id=lesson_id,
#             user_id=user_id
#         )
#         session.add(db_history_learning)
#         await session.commit()
#         await session.refresh(db_history_learning)
#         return db_history_learning


# async def get_history_learnings_by_user(user_id: int):
#     """Получить все записи истории обучения для определенного пользователя."""
#     async with async_session_maker() as session:  # Открываем сессию
#         result = await session.execute(select(History_learning).filter(History_learning.user_id == user_id))
#         return result.scalars().all()


# async def update_history_learning(history_learning_id: int, voice_text: str = None, audio_id_bot: str = None,
#                                   method_learning_id: int = None, word_id: int = None,
#                                   lesson_id: int = None, user_id: int = None):
#     """Обновить информацию в записи истории обучения."""
#     async with async_session_maker() as session:  # Открываем сессию
#         result = await session.execute(select(History_learning).filter(History_learning.id == history_learning_id))
#         db_history_learning = result.scalars().first()
#         if not db_history_learning:
#             raise NoResultFound(f"History learning record with id {history_learning_id} not found")

#         if voice_text:
#             db_history_learning.voice_text = voice_text
#         if audio_id_bot:
#             db_history_learning.audio_id_bot = audio_id_bot
#         if method_learning_id:
#             db_history_learning.method_learning_id = method_learning_id
#         if word_id:
#             db_history_learning.word_id = word_id
#         if lesson_id:
#             db_history_learning.lesson_id = lesson_id
#         if user_id:
#             db_history_learning.user_id = user_id

#         await session.commit()
#         await session.refresh(db_history_learning)
#         return db_history_learning


# async def delete_history_learning(history_learning_id: int):
#     """Удалить запись истории обучения по её id."""
#     async with async_session_maker() as session:  # Открываем сессию
#         result = await session.execute(select(History_learning).filter(History_learning.id == history_learning_id))
#         db_history_learning = result.scalars().first()
#         if db_history_learning:
#             await session.delete(db_history_learning)
#             await session.commit()
#         return db_history_learning


# === Method Learning CRUD ===

async def create_method_learning(name: str):
    """Создать метод обучения."""
    async with async_session_maker() as session:  # Открываем сессию
        db_method_learning = Method_learning(name=name)
        session.add(db_method_learning)
        await session.commit()
        await session.refresh(db_method_learning)
        return db_method_learning


async def get_all_method_learnings():
    """Получить все методы обучения."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Method_learning))
        return result.scalars().all()


async def get_method_learning_by_id(method_learning_id: int):
    """Получить метод обучения по его id."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Method_learning).filter(Method_learning.id == method_learning_id))
        return result.scalars().first()


async def update_method_learning(method_learning_id: int, name: str = None):
    """Обновить информацию о методе обучения."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Method_learning).filter(Method_learning.id == method_learning_id))
        db_method_learning = result.scalars().first()
        if not db_method_learning:
            raise NoResultFound(
                f"Method learning with id {method_learning_id} not found")

        if name:
            db_method_learning.name = name

        await session.commit()
        await session.refresh(db_method_learning)
        return db_method_learning


async def delete_method_learning(method_learning_id: int):
    """Удалить метод обучения по его id."""
    async with async_session_maker() as session:  # Открываем сессию
        result = await session.execute(select(Method_learning).filter(Method_learning.id == method_learning_id))
        db_method_learning = result.scalars().first()
        if db_method_learning:
            await session.delete(db_method_learning)
            await session.commit()
        return db_method_learning


################## METHODS HISTORY VIEWS WORD ########################

async def create_history_views_word(word_id: int, lesson_id: int, user_id: int):
    """Создать новую запись в истории просмотра слов."""
    async with async_session_maker() as session:
        db_history_view_word = History_views_word(
            word_id=word_id,
            lesson_id=lesson_id,
            user_id=user_id
        )
        session.add(db_history_view_word)
        await session.commit()
        await session.refresh(db_history_view_word)
        return db_history_view_word


async def get_history_views_by_lesson_and_word(lesson_id: int, word_id: int, user_id: int):
    """Получить записи истории по уроку и слову."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(History_views_word).filter(
                History_views_word.lesson_id == lesson_id
            ).filter(
                History_views_word.word_id == word_id
            ).filter(
                History_views_word.user_id == user_id
            )
        )
        return result.scalars().all()


async def get_all_direction_translation():
    """Получить все направления перевода с именами языков"""
    async with async_session_maker() as session:
        stmt = select(Direction_translation).options(
            joinedload(Direction_translation.language_input),
            joinedload(Direction_translation.language_output)
        )
        result = await session.execute(stmt)
        return result.unique().scalars().all()


async def get_direction_translation_by_id(direction_id: int):
    """Получить направление перевода по id с именами языков"""
    async with async_session_maker() as session:
        stmt = select(Direction_translation).where(
            Direction_translation.id == direction_id
        ).options(
            joinedload(Direction_translation.language_input),
            joinedload(Direction_translation.language_output)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
