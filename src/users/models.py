from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from config import settings

from .utils import file_name, validate_image


class Profile(AbstractUser):
    avatar = models.ImageField(
        upload_to=file_name,
        blank=True,
        validators=[validate_image],
        verbose_name=_("Аватар (не более 50kb)")
    )

    def get_avatar_or_plug(self):
        plug = static(settings.DEFAULT_AVATAR_PATH)
        return self.avatar if self.avatar else plug
