import json
import os

import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from dotenv import load_dotenv, find_dotenv

from .forms import LoginForm
from .models import UserPlus

load_dotenv(find_dotenv())


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'


@csrf_exempt
def flash_call(request):
    phone_number = json.loads(request.body)

    url = "https://zvonok.com/manager/cabapi_external/api/v1/phones/flashcall/"

    payload = {'public_key': os.getenv('ZVONOK_PUBLIC_KEY'),
               'phone': phone_number,
               'campaign_id': os.getenv('ZVONOK_CAMPAIGN_ID')}

    response = requests.request("POST", url, data=payload)
    return JsonResponse(eval(response.text))


@csrf_exempt
def register(request):
    if request.method == "POST":

        data = request.POST
        user = get_user_model().objects.create_user(username=data['phone_number'], password=data["password"])
        user.last_name = data['last_name']
        user.first_name = data['first_name']
        user.save()

        UserPlus.objects.create(user_id=user, patronymic=data['patronymic'])

        return redirect("users:login", permanent=True)

    return render(request, 'users/register.html')
