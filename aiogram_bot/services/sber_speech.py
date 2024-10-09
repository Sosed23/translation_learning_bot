import requests
from services.access.token_sber_speech import get_access_token

# URL API с параметрами
url = "https://smartspeech.sber.ru/rest/v1/text:synthesize?format=opus&voice=Kin_24000"

access_token = get_access_token()

# Заголовки
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/text"
}


def get_speech(en_word: str):

    response = requests.post(url, headers=headers, data=en_word, verify=False)

    word = en_word

    if response.status_code == 200:

        with open(f"storage/audios/{word}.opus", "wb") as file:
            file.write(response.content)
        print("Аудио успешно сохранено в файл")
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")

    return response


# get_speech(en_word="Hello, how's your mood? What will you be doing tomorrow?")
