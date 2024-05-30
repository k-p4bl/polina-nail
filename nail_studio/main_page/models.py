from django.db import models
from django.utils import timezone


class ServiceForHtml(models.Model):
    objects = models.Manager()
    service = models.CharField(max_length=50, verbose_name='Услуга')
    time_to_comp = models.CharField(max_length=50, verbose_name='Время выполнения в часах')
    price = models.IntegerField(verbose_name='Стоимость')
    prepayment = models.IntegerField(verbose_name='Предоплата')
    filming_work = models.IntegerField(verbose_name='Снятие чужой работы')
    image = models.ImageField(upload_to='main_page/images/for_service/', verbose_name='Фото')

    def __str__(self):
        return self.service

    class Meta:
        ordering = ['id']
        verbose_name = 'Услугу, отображаемую на сайте'
        verbose_name_plural = 'Услуги, отображаемые на сайте'

    def get_time_to_comp(self):
        seconds = int(float(self.time_to_comp) * 3600)
        h = seconds // 3600
        m = seconds % 3600 // 60
        return [h, m]


class AdditionalServiceForHtml(models.Model):
    objects = models.Manager
    service = models.CharField(max_length=50, verbose_name='Услуга')
    price = models.IntegerField(verbose_name='Стоимость')

    def __str__(self):
        return self.service

    class Meta:
        ordering = ['id']
        verbose_name = 'Доп. услугу'
        verbose_name_plural = 'Доп. услуги, отображаемые на сайте'
