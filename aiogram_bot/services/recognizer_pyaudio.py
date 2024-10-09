import speech_recognition as sr
import sys


sys.stdout.reconfigure(encoding='utf-8')

# Инициализация распознавателя
recognizer = sr.Recognizer()

# Использование микрофона для захвата речи
with sr.Microphone() as source:
    print("Скажите что-нибудь...")
    audio = recognizer.listen(source)

    # Распознавание речи с использованием Google Web Speech API
    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        print(f"Вы сказали: {text}")
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
    except sr.RequestError as e:
        print(f"Ошибка сервиса; {e}")
