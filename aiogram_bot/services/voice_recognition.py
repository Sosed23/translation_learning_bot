import speech_recognition as sr
from pydub import AudioSegment
import io

# Инициализация распознавателя
recognizer = sr.Recognizer()


def recognize_speech_from_voice(voice_file):
    try:
        # Конвертация аудио из OGG в WAV
        audio = AudioSegment.from_file(voice_file, format="ogg")

        # Используем BytesIO вместо временного файла на диске
        wav_audio = io.BytesIO()
        audio.export(wav_audio, format="wav")
        wav_audio.seek(0)  # Сбрасываем указатель на начало файла

        # Использование speech_recognition для распознавания
        with sr.AudioFile(wav_audio) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ru-RU")

        return text

    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Ошибка сервиса: {e}"
    except Exception as e:
        # Дополнительная обработка неизвестных ошибок
        return f"Произошла ошибка: {e}"
