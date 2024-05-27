import json
from pathlib import Path

from app import APP_DIR


def parse_photos_info():
    path = Path(APP_DIR).parent / 'photos_info.json'
    with open(path, encoding="UTF-8") as f:
        data = json.load(f)
        photos_info = data['photos']
    return photos_info


def parse_photos_descriptions():
    photos_info = parse_photos_info()
    url_description_dict = {photo['url']: photo['description'] for photo in photos_info}
    return url_description_dict
