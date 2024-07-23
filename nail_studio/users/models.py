from django.contrib.auth import get_user_model
from django.db import models


class UserPlus(models.Model):
    objects = models.Manager
    user_id = models.OneToOneField(get_user_model(), models.CASCADE)
    patronymic = models.CharField(max_length=255, verbose_name="Отчество", null=True)

