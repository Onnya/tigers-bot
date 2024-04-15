from app import client, processor, model
from transformers.utils import reshape


def extract_image_vector(photo):
    inputs = processor(images=photo, return_tensors="pt")
    outputs = model(**inputs)

    return reshape(outputs.pooler_output, [-1])


def find_similar_photo(image_vector):
    search_results = client.search(
        collection_name="tigers_collection", query_vector=image_vector, limit=3
    )

    return search_results # дописать отправку самого вероятного
