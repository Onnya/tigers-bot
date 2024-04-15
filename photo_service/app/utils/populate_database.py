import json
from app.utils.image_processing import extract_image_vector


def populate_database(): # проверять и заполнять векторную бд и бд с описаниями
    with open('photo_paths.json') as f:
        data = json.load(f)
        photos_info = data['photos']

    for photo_info in photos_info:
        photo_path = photo_info['path']
        photo_description = photo_info['description']

        photo_vector = extract_image_vector(photo_path)


if __name__ == '__main__':
    populate_database()
