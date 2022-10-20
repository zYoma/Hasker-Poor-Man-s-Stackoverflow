import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from config import settings


class Profile(AbstractUser):
    def validate_image(fieldfile_obj):
        filesize = fieldfile_obj.file.size
        kilobyte_limit = settings.AVATAR_MAX_SIZE_KB
        if filesize > kilobyte_limit * 1024:
            raise ValidationError("Максимальный размер изображения %s Kbyte" % str(kilobyte_limit))

    def file_name(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (instance.username, ext)
        fullname = os.path.join(settings.MEDIA_ROOT, 'avatars/', filename)
        if os.path.exists(fullname):
            os.remove(fullname)

        return 'avatars/' + filename

    avatar = models.ImageField(
        upload_to=file_name,
        blank=True,
        validators=[validate_image],
        verbose_name=_("Аватар (не более 50kb)")
    )
