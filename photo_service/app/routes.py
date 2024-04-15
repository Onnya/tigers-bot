from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
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

    photo = photo_obj.read()
    photo_mimetype = photo_obj.content_type

    #image_vector = extract_image_vector(photo)

    #similar_photo = find_similar_photo(image_vector)
    similar_photo = photo
    return send_file(
        BytesIO(similar_photo),
        mimetype=photo_mimetype,
        as_attachment=True,
        download_name=f"tiger-{photo_filename}"
    ), 200
