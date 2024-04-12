from flask import Flask
from app.routes import upload_photo_blueprint

app = Flask(__name__)

app.register_blueprint(upload_photo_blueprint)
