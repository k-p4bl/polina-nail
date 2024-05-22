from django.db import models
from django.utils import timezone


# TODO delete
# ______________________________________________________________________________________________________________________
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

    def __str__(self):
        return str(self.start_date) + ':' + str(self.finish_date)

    class Meta:
        ordering = ['start_date']
        verbose_name = 'Диапазон недоступных дат'
        verbose_name_plural = 'Диапазоны недоступных дат'
# ______________________________________________________________________________________________________________________


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


# TODO delete
# ______________________________________________________________________________________________________________________
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


class DateManager(models.Manager):
    def get_dates_with_three_times(self):
        list_of_date = []
        for obj in self.filter(date__gte=timezone.localdate()).annotate(models.Count('time')):
            if obj.time__count >= Time.objects.count():
                list_of_date.append(obj.date.strftime('%Y-%m-%d'))
        return list_of_date


class Date(models.Model):
    DoesNotExist = None
    objects = DateManager()
    date = models.DateField(verbose_name='Дата')
    time = models.ManyToManyField(Time, verbose_name='Время')

    def __str__(self):
        return self.date.strftime('%d.%m.%Y')

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['date'])
        ]
        verbose_name = 'Дату записи'
        verbose_name_plural = 'Даты записей'


class Service(models.Model):
    objects = models.Manager()
    service = models.CharField(max_length=50, unique=True, verbose_name='Услуга')

    def __str__(self):
        return self.service

    class Meta:
        verbose_name = 'Услугу'
        verbose_name_plural = 'Услуги'


class PersonName(models.Model):
    objects = models.Manager()
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    patronymic = models.CharField(max_length=100, verbose_name='Отчество')
    phone_number = models.CharField(max_length=20, verbose_name='Номер телефона')
    date = models.ForeignKey(to=Date, on_delete=models.PROTECT, verbose_name='Дата')
    time = models.ForeignKey(to=Time, on_delete=models.PROTECT, verbose_name='Время')
    service = models.ForeignKey(to=Service, on_delete=models.PROTECT, verbose_name='Услуга')

    def __str__(self):
        return self.last_name

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

# ______________________________________________________________________________________________________________________
