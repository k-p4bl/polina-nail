import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from .models import PersonDataAndDate, Service, Time, AdditionalService
from main_page.models import ServiceForHtml


class SignUpErrorList(ErrorList):
    def __str__(self):
        return self.as_text()


class ServiceChoiceField(forms.ModelChoiceField):
    def to_python(self, value):
        return Service.objects.get_or_create(service=value)[0]


class SignUpForm(forms.Form):
    service = ServiceChoiceField(queryset=ServiceForHtml.objects.all(),
                                 empty_label='Выберите услугу',
                                 to_field_name='service',
                                 label='Услуга',
                                 widget=forms.Select(attrs={'id': "service"})
                                 )

    add_service = forms.MultipleChoiceField(
        # choices=[(i.pk, i) for i in AdditionalService.objects.all()],
        # choices=[(0, 'Снятие чужой работы'), (1, 'Дизайн'),
        #          (2, 'Парафинотерапия')],
        label='Доп. услуга',
        required=False
    )
    # add_service = forms.MultipleChoiceField(choices=[i.add_service for i in AdditionalService.objects.all()])

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

    date = forms.DateField(widget=forms.DateInput(attrs={'type': "date",
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
        p = PersonDataAndDate.objects.filter(date=self.cleaned_data['date'])
        lst = []
        for i in p:
            lst.append(i.time)
        time = self.cleaned_data['time']
        if time in lst:
            raise ValidationError('К сожалению это время уже занято')
        return time


class SignUpAdminForm(forms.ModelForm):
    class Meta:
        model = PersonDataAndDate
        fields = ['service', 'additional_service', 'last_name', 'first_name', 'patronymic', 'phone_number', 'date',
                  'time', 'user_id']

    def clean_time(self):
        persons_qs = PersonDataAndDate.objects.filter(date=self.cleaned_data['date'])
        busy_time_lst = []
        for person in persons_qs:
            if self.initial:
                if person.time.pk == self.initial['time']:
                    continue
            busy_time_lst.append(person.time)
        new_time = self.cleaned_data['time']
        if new_time in busy_time_lst:
            raise ValidationError('К сожалению это время уже занято')
        return new_time
