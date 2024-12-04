import base64
import binascii
import os
from uuid import uuid4
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def check_is_base64(base64_string: str) -> bool:
    try:
        base64.b64decode(base64_string.split(';base64,')[-1], validate=True)
        return True
    except (ValueError, binascii.Error):
        return False


def base64_to_file(base64_string: str, name: str = 'image') -> ContentFile:
    try:
        format, file_str = base64_string.split(';base64,')
        ext = format.split('/')[-1]
        file_name = f'{name}-{uuid4().hex}.{ext}'

        file_path = os.path.join('icon', file_name)
        file_content = ContentFile(base64.b64decode(file_str))

        saved_path = default_storage.save(file_path, file_content)
        return saved_path
    except Exception as e:
        raise ValueError(f"Invalid base64 string: {e}")


def delete_old_file(instance, field: str) -> None:
    file_field = getattr(instance, field, None)
    if file_field:
        file_field.delete(save=False)
