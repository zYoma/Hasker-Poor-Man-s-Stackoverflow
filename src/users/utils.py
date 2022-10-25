from django.core.exceptions import ValidationError
from django.utils import timezone

from config import settings


def validate_image(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    kilobyte_limit = settings.AVATAR_MAX_SIZE_KB
    if filesize > kilobyte_limit * 1024:
        raise ValidationError(f"Максимальный размер изображения {kilobyte_limit} Kbyte")


def file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.id}/{timezone.now()}.{ext}"
    return 'avatars/' + filename
