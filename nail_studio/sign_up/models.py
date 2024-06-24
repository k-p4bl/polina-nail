from django.db import models


class Time(models.Model):
    objects = models.Manager()
    time = models.TimeField(unique=True, verbose_name='Время')

    def __str__(self):
        return self.time.strftime('%H:%M')

    class Meta:
        ordering = ['time']
        indexes = [
            models.Index(fields=['time'])
        ]
        verbose_name = 'Время записи'
        verbose_name_plural = 'Время записей'


class Service(models.Model):
    objects = models.Manager()
    service = models.CharField(max_length=50, unique=True, verbose_name='Услуга')

    def __str__(self):
        return self.service

    class Meta:
        verbose_name = 'Услугу'
        verbose_name_plural = 'Услуги'


class AdditionalService(models.Model):
    objects = models.Manager()
    add_service = models.CharField(max_length=50, verbose_name='Доп. услуга')
    price = models.IntegerField(verbose_name='Стоимость')

    def __str__(self):
        return self.add_service

    class Meta:
        verbose_name = 'Доп. услугу'
        verbose_name_plural = 'Доп. услуги'


class PersonDataAndDate(models.Model):
    objects = models.Manager()
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    patronymic = models.CharField(max_length=100, verbose_name='Отчество')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    date = models.DateField(verbose_name='Дата')
    time = models.ForeignKey(to=Time, on_delete=models.PROTECT, verbose_name='Время')
    service = models.ForeignKey(to=Service, on_delete=models.PROTECT, verbose_name='Услуга')
    additional_service = models.ManyToManyField(AdditionalService, blank=True, verbose_name='Дополнительные услуги')
    payment_id = models.CharField(max_length=255, verbose_name='id платежа предоплаты', null=True, blank=True,
                                  editable=False)

    def __str__(self):
        return self.last_name

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'


class DisabledDatesManager(models.Manager):
    def get_disabled_dates(self):
        list_of_date = []
        for date in self.model.objects.all():
            if date.finish_date is not None:
                list_of_date.append(date.start_date.strftime('%Y-%m-%d') + ':' + date.finish_date.strftime('%Y-%m-%d'))
            else:
                list_of_date.append(date.start_date.strftime('%Y-%m-%d'))
        return list_of_date


class DisabledDates(models.Model):
    objects = DisabledDatesManager()
    start_date = models.DateField(verbose_name='Начало диапазона/Недоступная дата')
    finish_date = models.DateField(null=True, blank=True, verbose_name='Конец диапазона')
    creator_is_human = models.BooleanField(default=True, editable=False, verbose_name='Создано человеком')

    def __str__(self):
        return str(self.start_date) + ':' + str(self.finish_date)

    class Meta:
        ordering = ['start_date']
        verbose_name = 'Диапазон недоступных дат'
        verbose_name_plural = 'Диапазоны недоступных дат'
