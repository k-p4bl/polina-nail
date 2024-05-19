from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import LoginForm


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'


