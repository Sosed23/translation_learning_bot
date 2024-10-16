import requests
from services.access.token_sber_speech import get_access_token


def get_speech(en_word: str):
    url = "https://smartspeech.sber.ru/rest/v1/text:synthesize?format=opus&voice=Kin_24000"

    # Получение токена
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/text"
    }

    response = requests.post(url, headers=headers, data=en_word, verify=False)

    if response.status_code == 200:
        with open(f"storage/audios/{en_word}.opus", "wb") as file:
            file.write(response.content)
        print("Аудио успешно сохранено в файл")
    elif response.status_code == 401:
        # Обработка ошибки истечения токена
        print("Токен истек, обновляем...")
        access_token = get_access_token()
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.post(url, headers=headers,
                                 data=en_word, verify=False)
        if response.status_code == 200:
            with open(f"storage/audios/{en_word}.opus", "wb") as file:
                file.write(response.content)
            print("Аудио успешно сохранено в файл после обновления токена")
        else:
            print(
                f"Ошибка после обновления токена: {response.status_code}, {response.text}")
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")

    return response
