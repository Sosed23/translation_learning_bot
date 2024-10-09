from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, BigInteger, func, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())


class Base_created(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str] = mapped_column(String(13), nullable=True)


class Lesson(Base):
    __tablename__ = 'lessons'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    user: Mapped['User'] = relationship(backref='lessons')


class Language(Base):
    __tablename__ = 'languages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)


class Direction_translation(Base):
    __tablename__ = 'direction_translations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)

    language_input_id: Mapped[int] = mapped_column(ForeignKey(
        'languages.id', ondelete='CASCADE'), nullable=False)
    language_input: Mapped['Language'] = relationship(
        'Language', foreign_keys=[language_input_id], backref='direction_input')

    language_output_id: Mapped[int] = mapped_column(ForeignKey(
        'languages.id', ondelete='CASCADE'), nullable=False)
    language_output: Mapped['Language'] = relationship(
        'Language', foreign_keys=[language_output_id], backref='direction_output')


class Word(Base):
    __tablename__ = 'words'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    translation: Mapped[str] = mapped_column(String(500), nullable=False)
    transcription: Mapped[str] = mapped_column(String(500), nullable=False)
    image_id_bot: Mapped[str] = mapped_column(String(500), nullable=True)

    audio_id_bot: Mapped[str] = mapped_column(String(500), nullable=True)

    language_id: Mapped[int] = mapped_column(ForeignKey(
        'languages.id', ondelete='CASCADE'), nullable=False)
    language: Mapped['Language'] = relationship(backref='words')
    lesson_id: Mapped[int] = mapped_column(ForeignKey(
        'lessons.id', ondelete='CASCADE'), nullable=False)
    lesson: Mapped['Lesson'] = relationship(backref='words')
    user_id: Mapped[int] = mapped_column(ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    user: Mapped['User'] = relationship(backref='words')


class Method_learning(Base):
    __tablename__ = 'method_learnings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)


class History_learning(Base):
    __tablename__ = 'history_learnings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    voice_text: Mapped[str] = mapped_column(String(500), nullable=True)
    audio_id_bot: Mapped[str] = mapped_column(String(500), nullable=True)

    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    method_learning_id: Mapped[int] = mapped_column(ForeignKey(
        'method_learnings.id', ondelete='CASCADE'), nullable=False)
    method_learning: Mapped['Method_learning'] = relationship(
        backref='history_learnings')

    word_id: Mapped[int] = mapped_column(ForeignKey(
        'words.id', ondelete='CASCADE'), nullable=False)
    word: Mapped['Word'] = relationship(backref='history_learnings')

    lesson_id: Mapped[int] = mapped_column(ForeignKey(
        'lessons.id', ondelete='CASCADE'), nullable=False)
    lesson: Mapped['Lesson'] = relationship(backref='history_learnings')

    user_id: Mapped[int] = mapped_column(ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    user: Mapped['User'] = relationship(backref='history_learnings')


class History_views_word(Base):
    __tablename__ = 'history_views_words'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    word_id: Mapped[int] = mapped_column(ForeignKey(
        'words.id', ondelete='CASCADE'), nullable=False)
    word: Mapped['Word'] = relationship(backref='history_views_words')

    lesson_id: Mapped[int] = mapped_column(ForeignKey(
        'lessons.id', ondelete='CASCADE'), nullable=False)
    lesson: Mapped['Lesson'] = relationship(backref='history_views_words')

    user_id: Mapped[int] = mapped_column(ForeignKey(
        'users.id', ondelete='CASCADE'), nullable=False)
    user: Mapped['User'] = relationship(backref='history_views_words')
