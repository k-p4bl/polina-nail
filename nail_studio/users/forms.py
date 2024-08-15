import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _

from sign_up.models import Time, PersonDataAndDate


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        "data-tel-input": ""
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    error_messages = {
        "invalid_login": "Пожалуйста, введите правильные номер телефона и пароль. Пароль может быть чувствителен к "
                         "регистру.",
        "inactive": _("This account is inactive."),
    }

    def clean_username(self):
        phone_number: str = self.cleaned_data["username"]
        if phone_number[0] == '8':
            phone_number = phone_number.replace('8', '+7')
        phone_number = re.sub(r"\s\W|\W\s|-", "", phone_number)
        return phone_number


class MoveSignUpErrorList(ErrorList):
    def __str__(self):
        return self.as_text()


class MoveSignUp(forms.Form):
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

    def clean_time(self):
        p = PersonDataAndDate.objects.filter(date=self.cleaned_data['date'])
        lst = []
        for i in p:
            lst.append(i.time)
        time = self.cleaned_data['time']
        if time in lst:
            raise ValidationError('К сожалению это время уже занято')
        return time
