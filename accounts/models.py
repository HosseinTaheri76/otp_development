from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):

    def _create_user(self, phone_number, password, **other_fields):
        user = self.model(phone_number=phone_number, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, phone_number, password=None, **other_fields):
        other_fields.setdefault('is_staff', False)
        other_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **other_fields)

    def create_superuser(self, phone_number, password=None, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        return self._create_user(phone_number, password, **other_fields)


class CustomUser(AbstractUser):
    phone_number = models.CharField(
        unique=True,
        max_length=11,
        validators=[RegexValidator('^09[0-9]{9}$', 'not a valid phone number.')],
        db_index=True
    )
    username = None
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
