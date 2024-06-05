from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from guest_user.functions import is_guest_user

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=50, blank=False, null=False)
    acknowledgement = models.BooleanField(_("acknowledgement"), default=True)
    followup_consent = models.BooleanField(_("followup_consent"), default=True)
    future_contact = models.BooleanField(_("future_contact"), default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    readonly_fields = (
      "is_guest",
    )

    @property
    def is_guest(self):
        return is_guest_user(self)

    def __str__(self):
        return self.email
