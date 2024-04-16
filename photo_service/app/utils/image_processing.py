from app import client, processor, model
from transformers.utils import reshape
from os.path import join, dirname, abspath


def extract_image_vector(photo):
    inputs = processor(images=photo, return_tensors="pt")
    outputs = model(**inputs)

    return reshape(outputs.pooler_output, [-1])


def find_similar_photo(image_vector):
    collection_name = "tigers_collection"
    search_results = client.search(
        collection_name=collection_name, query_vector=image_vector, limit=3
    )

    most_similar_url = search_results[0].payload["url"]
    current_directory = dirname(abspath(__file__))
    photo_path = join(current_directory, '..', '..', 'photos', most_similar_url)
    return photo_path
