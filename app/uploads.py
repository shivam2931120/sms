import os
from datetime import datetime

from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_PHOTO_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


def save_student_photo(student, photo):
    if not photo or not photo.filename:
        return None

    original_name = secure_filename(photo.filename)
    extension = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
    if extension not in ALLOWED_PHOTO_EXTENSIONS:
        raise ValueError('Photo must be a JPG, PNG, or WEBP file.')

    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = f"student_{student.id}_{timestamp}_{original_name}"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'photos')
    os.makedirs(upload_dir, exist_ok=True)
    photo.save(os.path.join(upload_dir, filename))
    student.photo_file = filename
    return filename
