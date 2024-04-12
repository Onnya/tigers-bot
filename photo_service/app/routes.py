from flask import Blueprint, request, jsonify

upload_photo_blueprint = Blueprint('upload_photo', __name__)


@upload_photo_blueprint.route('/upload-photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400

    photo = request.files['photo']

    if photo.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Далее можно сохранить файл или обработать его, как требуется
    # Например, сохранить в файловую систему или обработать изображение

    return jsonify({'message': 'Photo uploaded successfully'}), 200
