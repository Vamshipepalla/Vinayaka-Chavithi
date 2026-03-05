"""Utility functions for file handling, validation, and sanitization."""
import os
import re
import uuid
from werkzeug.utils import secure_filename

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXT = {'mp4', 'webm', 'ogg'}


def sanitize_input(value: str) -> str:
    if not value:
        return ''
    value = str(value).strip()
    value = re.sub(r'<script[^>]*?>.*?</script>', '', value, flags=re.DOTALL | re.IGNORECASE)
    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
    return value[:5000]


def validate_phone(phone: str) -> bool:
    return bool(re.fullmatch(r'[6-9]\d{9}', phone.replace(' ', '').replace('-', '')))


def validate_email(email: str) -> bool:
    return bool(re.fullmatch(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', email))


def allowed_image(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXT


def allowed_video(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXT


def save_upload(file_obj, upload_folder: str, subfolder: str = '') -> str | None:
    """Save an uploaded file and return relative path for url_for('static', filename=...)"""
    try:
        from flask import current_app
        filename = secure_filename(file_obj.filename)
        ext = filename.rsplit('.', 1)[-1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        dest_folder = os.path.join(current_app.root_path, upload_folder, subfolder)
        os.makedirs(dest_folder, exist_ok=True)
        full_path = os.path.join(dest_folder, unique_name)
        file_obj.save(full_path)

        # Build path relative to 'static/' folder only
        rel = os.path.join(upload_folder, subfolder, unique_name).replace('\\', '/')
        if rel.startswith('static/'):
            rel = rel[len('static/'):]
        return rel

    except Exception as e:
        print(f"[ERROR] save_upload: {e}")
        return None


def resize_image(full_path: str, max_w: int, max_h: int):
    if not PIL_AVAILABLE or not os.path.exists(full_path):
        return
    try:
        with Image.open(full_path) as img:
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            img.save(full_path, optimize=True, quality=85)
    except Exception as e:
        print(f"[WARN] resize_image: {e}")