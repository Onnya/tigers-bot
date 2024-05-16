from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from PIL import Image
from app.utils.image_processing import extract_image_vector, find_similar_photo

upload_photo_blueprint = Blueprint('upload_photo', __name__)


@upload_photo_blueprint.route('/upload-photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400

    photo_obj = request.files['photo']

    photo_filename = photo_obj.filename

    if photo_filename == '':
        return jsonify({'error': 'No selected file'}), 400

    photo_bytes = photo_obj.read()
    photo = Image.open(BytesIO(photo_bytes))
    photo_mimetype = photo_obj.content_type

    image_vector = extract_image_vector(photo)
    similar_photo_url, similar_photo_description = find_similar_photo(image_vector)

    file_response = send_file(
        similar_photo_url,
        mimetype=photo_mimetype,
        as_attachment=True,
        download_name=f"tiger-{photo_filename}"
    )

    file_response.headers['X-Photo-Description'] = similar_photo_description

    return file_response, 200
