from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, verbose_name="username", blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name="Email", help_text="Введите Ваш e-mail")
    avatar = models.ImageField(upload_to="media/users/avatars/", verbose_name='Аватар', blank=True, null=True, help_text="Загрузите Ваше фото")
    phone_number = models.CharField(max_length=35, verbose_name="Телефон", blank=True, null=True,
                             help_text="Введите номер телефона")
    country = models.CharField(max_length=100, verbose_name="Страна", blank=True, null=True,
                               help_text="Введите Вашу страну")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username",]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
