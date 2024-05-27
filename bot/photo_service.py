import requests
from urllib.parse import unquote


def get_photo(photo):
    app_url = "http://flask_app:5000"
    url = f"{app_url}/upload-photo"

    response = requests.post(url, files={'photo': photo})

    if response.status_code == 200:
        photo = response.content
        encoded_text = response.headers.get('X-Photo-Description', 'No description')
        description = unquote(encoded_text)
        return photo, description
    else:
        print("Ошибка при получении фотографии:", response.status_code)
        return None, ""
