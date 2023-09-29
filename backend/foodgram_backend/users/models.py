from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username

ROLE_LENGTH = 30
EMAIL_LENGTH = 254
USERNAME_LENGTH = 150


USERS_ROLES = (
    ('admin', 'admin'),
    ('user', 'user'),
)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'password'
    ]
    username = models.CharField(
        validators=(validate_username,),
        max_length=USERNAME_LENGTH,
        unique=True,
        verbose_name='Username'
    )
    role = models.CharField(
        max_length=ROLE_LENGTH,
        choices=USERS_ROLES,
        default='user',
        blank=True
    )
    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
        verbose_name='Email',
        blank=True,
        default='default@ya.ru'
    )
    first_name = models.CharField(
        max_length=USERNAME_LENGTH,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USERNAME_LENGTH,
        blank=True,
        verbose_name='Фамилия'
    )

    @property
    def is_admin(self):
        return self.role == 'admin'

    class Meta:
        ordering = ('id',)
