from pathlib import Path
import uuid

from PIL import Image
from qdrant_client import models

from app.utils.image_processing import extract_image_vector
from app.utils.parse_photos_json import parse_photos_info
from app import client, vectors_config, APP_DIR


def populate_database(clear_collection=False):
    collection_name = "tigers_collection"

    if clear_collection:
        clear_collection_data(collection_name)

    create_collection_if_not_exist(collection_name)

    new_points = parse_photos_info()
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


def push_points(collection_name, points):
    new_points = []
    for point in points:
        url = point["url"]
        if not vector_exists(collection_name, url):
            photo_path = Path(APP_DIR).parent / 'photos' / url
            photo = Image.open(photo_path)
            vector = extract_image_vector(photo)
            point = get_point(vector, url)
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


def get_point(vector, url):
    vector_id = str(uuid.uuid4())
    return models.PointStruct(id=vector_id, vector=vector, payload={"url": url})


if __name__ == '__main__':
    populate_database()
