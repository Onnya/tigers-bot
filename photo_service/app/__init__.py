from os.path import abspath, dirname
from os import getenv

from flask import Flask
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from transformers import AutoImageProcessor, AutoModel


app = Flask(__name__)

client = QdrantClient("http://qdrant", port=6333)
# client = QdrantClient("localhost", port=6333)
processor = AutoImageProcessor.from_pretrained('facebook/dinov2-base')
model = AutoModel.from_pretrained('facebook/dinov2-base')
vectors_config = VectorParams(size=768, distance=Distance.DOT)

APP_DIR = dirname(abspath(__file__))


from app.utils.parse_photos_json import parse_photos_descriptions


photos_descriptions = parse_photos_descriptions()


from app.utils.populate_database import populate_database


reload_vectors_flag = getenv('RELOAD_VECTORS', 'false').lower() == 'true'
clear_db_flag = getenv('CLEAR_DB', 'false').lower() == 'true'

if reload_vectors_flag:
    populate_database(clear_collection=clear_db_flag)


from app.routes import upload_photo_blueprint


app.register_blueprint(upload_photo_blueprint)
