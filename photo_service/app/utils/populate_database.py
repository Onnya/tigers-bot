import json
from PIL import Image
from qdrant_client import models
import uuid
from app.utils.image_processing import extract_image_vector
from app import client, vectors_config
from os.path import join, dirname, abspath


def populate_database(clear_collection=False):
    collection_name = "tigers_collection"
    current_directory = dirname(abspath(__file__))
    json_path = join(current_directory, '..', '..', 'photos_info.json')

    if clear_collection:
        clear_collection_data(collection_name)

    create_collection_if_not_exist(collection_name)

    new_points = parse_config_json(json_path)
    push_points(collection_name, new_points)


def clear_collection_data(collection_name):
    client.vectors.delete(collection_name)


def create_collection_if_not_exist(collection_name):
    collections = [collection.name for collection in client.get_collections().collections]
    if collection_name not in collections:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config
        )


def parse_config_json(path):
    with open(path, encoding="UTF-8") as f:
        data = json.load(f)
        photos_info = data['photos']
    return photos_info


def push_points(collection_name, points):
    current_directory = dirname(abspath(__file__))
    new_points = []
    for point in points:
        url = point["url"]
        if not vector_exists(collection_name, url):
            photo_path = join(current_directory, '..', '..', 'photos', url)
            photo = Image.open(photo_path)
            vector = extract_image_vector(photo)
            point = get_point(collection_name, vector, url)
            new_points.append(point)
    if new_points:
        client.upsert(collection_name, new_points)


def vector_exists(collection_name, url):
    vectors = client.scroll(
        collection_name=f"{collection_name}",
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="url", match=models.MatchValue(value=url)
                ),
            ],
        ),
    )

    return len(vectors[0]) > 0


def get_point(collection_name, vector, url):
    vector_id = str(uuid.uuid4())
    return models.PointStruct(id=vector_id, vector=vector, payload={"url": url})


if __name__ == '__main__':
    populate_database()
