from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.models.user_manager import UserManager


class User(AbstractUser):
    objects = UserManager()

    id = models.AutoField(primary_key=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        default='',
        verbose_name='username',
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[UnicodeUsernameValidator()],
        error_messages={'unique': 'A user with that username already exists.'},
    )
    email = models.EmailField(unique=True, blank=False)
    role = models.CharField(max_length=20, default='USER')
    address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    postal_code = models.CharField(max_length=20, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'auth_user'
        app_label = 'users'
