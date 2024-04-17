import requests


def get_photo(photo):
    url = "http://127.0.0.1:5000/upload-photo"

    response = requests.post(url, files={'photo': photo})

    if response.status_code == 200:
        return response.content
    else:
        print("Ошибка при получении фотографии:", response.status_code)
        return None
