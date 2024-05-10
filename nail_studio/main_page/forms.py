import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from main_page import models
from main_page.models import ServiceForHtml, Time


class SignUpErrorList(ErrorList):
    def __str__(self):
        return self.as_text()


class ServiceChoiceField(forms.ModelChoiceField):
    def to_python(self, value):
        return models.Service.objects.get_or_create(service=value)[0]


class DateModelField(forms.DateField):
    def to_python(self, value):
        return models.Date.objects.get_or_create(date=value)


class SignUpForm(forms.Form):
    service = ServiceChoiceField(queryset=ServiceForHtml.objects.all(),
                                 empty_label='Выберите услугу',
                                 to_field_name='service',
                                 label='Услуга',
                                 widget=forms.Select(attrs={'id': "service"})
                                 )

    person_name = forms.CharField(label='Ф.И.О', widget=forms.TextInput(attrs={'name': "person-name",
                                                                               'id': "person-name",
                                                                               'placeholder': "Иванов Иван Иванович"}))
    phone_number = forms.CharField(label='Номер телефона',
                                   max_length=18,
                                   widget=forms.TextInput(attrs={
                                       'name': "phone-number",
                                       'id': "phone-number",
                                       'data-tel-input': True
                                   }))

    date = DateModelField(widget=forms.DateInput(attrs={'type': "date",
                                                        'name': "date",
                                                        'id': "date"
                                                        }))

    time = forms.ModelChoiceField(queryset=Time.objects.all(),
                                  widget=forms.RadioSelect(attrs={
                                      'data-time-input': True,
                                      'name': "time",
                                      'class': "real-radio-time"
                                  }))

    def clean_person_name(self):
        name = self.cleaned_data['person_name']
        name_split = re.findall(r'[А-Я][а-я]+', name)
        if len(name_split) < 3:
            raise ValidationError('Имя в неверном формате')
        return name_split

    def clean_time(self):
        date = self.cleaned_data['date'][0]
        time = self.cleaned_data['time']
        if time in date.time.all():
            raise ValidationError('К сожалению это время уже занято')
        return time

