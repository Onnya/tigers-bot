from flask import Flask
from qdrant_client import QdrantClient
from transformers import AutoImageProcessor, AutoModel


app = Flask(__name__)

client = QdrantClient("localhost", port=6333)
processor = AutoImageProcessor.from_pretrained('facebook/dinov2-base')
model = AutoModel.from_pretrained('facebook/dinov2-base')


from app.routes import upload_photo_blueprint


app.register_blueprint(upload_photo_blueprint)
