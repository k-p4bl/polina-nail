import datetime
import json
import os
import locale

import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.timezone import localdate
from django.views.decorators.csrf import csrf_exempt

from dotenv import load_dotenv, find_dotenv

from integrations.google.calendar.calendar_client import GoogleCalendar
from integrations.yookassa.payments import YandexPayment
from main_page.models import ServiceForHtml
from sign_up.models import PersonDataAndDate, DisabledDates, Time
from .forms import LoginForm, MoveSignUp, MoveSignUpErrorList
from .models import UserPlus

load_dotenv(find_dotenv())


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'


@login_required
def login_not_staff(request):
    if request.method == "POST":
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            if user:
                login(request, user)
                if request.GET.get("next"):
                    return redirect(request.GET["next"], permanent=True)
                else:
                    return redirect("users:personal-account", permanent=True)
    else:
        form = LoginForm()
    return render(request, "users/login_not_staff.html", {'user': request.user, "form": form})


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

        UserPlus.objects.create(user_id=user, patronymic=data['patronymic'], not_baned=True)

        return redirect("users:login", permanent=True)

    return render(request, 'users/register.html')


@login_required
def personal_account(request):
    if request.user.is_staff:
        return render(request, "users/master_personal_account.html")
    phone = (request.user.username[0:2] + " (" + request.user.username[2:5] + ") " + request.user.username[5:8] +
             "-" + request.user.username[8:10] + "-" + request.user.username[10:12])
    context = {
        "last_name": request.user.last_name,
        "first_name": request.user.first_name,
        "patronymic": request.user.userplus.patronymic,
        "phone_number": phone,
    }
    return render(request, "users/personal_account.html", context)


@login_required
def refactor_personal_data(request):
    if request.method == "POST":
        user = get_user_model().objects.get(pk=request.user.pk)
        user.last_name = request.POST["last_name"]
        user.first_name = request.POST["first_name"]
        user.userplus.patronymic = request.POST["patronymic"]
        user.save()
        user.userplus.save()

        return redirect("users:personal-account")

    context = {
        "last_name": request.user.last_name,
        "first_name": request.user.first_name,
        "patronymic": request.user.userplus.patronymic,
    }
    return render(request, "users/refactor.html", context)


@login_required
def future_sign_ups(request):
    now = timezone.localtime()
    f_sign_ups = request.user.persondataanddate_set.filter(date__gte=datetime.date(now.year, now.month, now.day))

    return render(request, "users/future_sign_ups.html", {"f_sign_ups": f_sign_ups})


@login_required
def past_sign_ups(request):
    now = timezone.localtime()
    p_sign_ups = request.user.persondataanddate_set.filter(date__lt=datetime.date(now.year, now.month, now.day))

    return render(request, "users/past_sign_ups.html", {"p_sign_ups": p_sign_ups})


@csrf_exempt
def forgot_password(request):
    if request.method == "POST":
        user = get_user_model().objects.get(username=request.POST['phone_number'])
        user.set_password(request.POST['password'])
        user.save()

        return redirect("users:login", permanent=True)

    return render(request, "users/forgot_password.html")


@csrf_exempt
def phone_check(request):
    phone = json.loads(request.body)
    for user in get_user_model().objects.all():
        if user.username == phone:
            return JsonResponse({'phone_is_busy': True})
    return JsonResponse({'phone_is_busy': False})


@login_required
def future_sign_up(request, pk):
    sign_up = PersonDataAndDate.objects.get(pk=pk)
    sign_up_datetime = datetime.datetime(year=sign_up.date.year, month=sign_up.date.month,
                                         day=sign_up.date.day, hour=sign_up.time.time.hour,
                                         minute=sign_up.time.time.minute)

    delta = sign_up_datetime - timezone.localtime().now()
    delta = delta.total_seconds() / 3600

    context = {
        "pk": pk,
        "sign_up": sign_up,
        "amount_value": YandexPayment.amount_value(sign_up.payment_id) if sign_up.payment_id else None,
        "less_than_a_day": False if delta > 24 else True
    }
    return render(request, "users/future_sign_up.html", context)


@login_required
def move_sign_up(request, pk):
    list_of_date = DisabledDates.objects.get_disabled_dates()
    service_html = ServiceForHtml.objects.all()

    sign_up = PersonDataAndDate.objects.get(pk=pk)

    if request.method == 'POST':
        form = MoveSignUp(request.POST, error_class=MoveSignUpErrorList)
        if form.is_valid():
            cd = form.cleaned_data
            calendar = GoogleCalendar()

            description = (f"{sign_up.phone_number} {sign_up.last_name} {sign_up.first_name} "
                           f"{sign_up.patronymic}")
            event = calendar.get_event(description, sign_up.date, sign_up.time.time)

            args = {'date': cd['date'],
                    'time': cd['time'].time,
                    'service': None,
                    'description': None,
                    'hour': None,
                    'minute': None}

            event.change(*args.values())

            try:
                DisabledDates.objects.get(start_date=sign_up.date, creator_is_human=False).delete()
            except DisabledDates.DoesNotExist:
                pass

            sign_up.date = cd['date']
            sign_up.time = cd['time']
            sign_up.save()

            if PersonDataAndDate.objects.filter(date=cd['date']).count() >= Time.objects.count():
                DisabledDates.objects.create(start_date=cd['date'], creator_is_human=False)

            return redirect("users:future_sign_up", pk)
    else:
        form = MoveSignUp(error_class=MoveSignUpErrorList)

    context = {
        'pk': pk,
        'sign_up': sign_up,
        'dates': list_of_date,
        'form': form,
        'ServiceForHtml': service_html,
    }

    return render(request, "users/move_sign_up.html", context)


@login_required
def delete_sign_up(request, pk):
    sign_up = PersonDataAndDate.objects.get(pk=pk)
    if request.method == "POST":
        if sign_up.payment_id:
            delta = sign_up.date - localdate()
            if delta.days >= 3:
                payment = YandexPayment()
                payment.refund_payment(sign_up.payment_id)

        calendar = GoogleCalendar()

        try:
            DisabledDates.objects.get(start_date=sign_up.date, creator_is_human=False).delete()
        except DisabledDates.DoesNotExist:
            pass
        description = f"{sign_up.phone_number} {sign_up.last_name} {sign_up.first_name} {sign_up.patronymic}"
        calendar.get_event(description, sign_up.date, sign_up.time.time).delete()
        sign_up.delete()

        return redirect("users:f_sign_ups")

    return render(request, "users/delete_sign_up.html", {'pk': pk, 'sign_up': sign_up})


@staff_member_required(login_url="users:login_not_staff")
def master_p_sign_ups(request):
    return render(request, "users/master_p_sign_ups.html")


@staff_member_required(login_url="users:login_not_staff")
def all_past_sign_ups(request):
    now = timezone.localtime()
    sign_ups = PersonDataAndDate.objects.filter(date__lt=datetime.date(now.year, now.month, now.day))
    dates = {}
    locale.setlocale(locale.LC_TIME, 'ru_RU')

    for s in sign_ups:
        if dates.get(s.date.strftime("%Y") + "г."):
            if dates.get(s.date.strftime("%Y") + "г.").get(s.date.strftime("%m") + " (" + s.date.strftime("%b") + ")"):
                if dates.get(s.date.strftime("%Y") + "г.").get(
                        s.date.strftime("%m") + " (" + s.date.strftime("%b") + ")").get(s.date.strftime("%d") + ", " +
                                                                                        s.date.strftime("%a")):
                    dates[s.date.strftime("%Y") + "г."][s.date.strftime("%m") + " (" + s.date.strftime("%b") + ")"][
                        s.date.strftime("%d") + ", " +
                        s.date.strftime("%a")][str(s.time.time.hour)] = str(s.pk)
                else:
                    dates[s.date.strftime("%Y") + "г."][s.date.strftime("%m") + " (" + s.date.strftime("%b") + ")"][
                        s.date.strftime("%d") + ", " +
                        s.date.strftime("%a")] = {str(s.time.time.hour): str(s.pk)}
            else:
                dates[s.date.strftime("%Y") + "г."][s.date.strftime("%m") + " (" + s.date.strftime("%b") + ")"] = {}
                dates[s.date.strftime("%Y") + "г."][s.date.strftime("%m") + " (" + s.date.strftime("%b") + ")"][
                    s.date.strftime("%d") + ", " +
                    s.date.strftime("%a")] = {str(s.time.time.hour): str(s.pk)}
        else:
            dates[s.date.strftime("%Y") + "г."] = {}
            dates[s.date.strftime("%Y") + "г."][s.date.strftime("%m") + " (" + s.date.strftime("%b") + ")"] = {}
            dates[s.date.strftime("%Y") + "г."][s.date.strftime("%m") + " (" + s.date.strftime("%b") + ")"][
                s.date.strftime("%d") + ", " +
                s.date.strftime("%a")] = {str(s.time.time.hour): str(s.pk)}
    return JsonResponse(dates)


@staff_member_required(login_url="users:login_not_staff")
def sign_up(request, pk):
    person_data = PersonDataAndDate.objects.get(pk=pk)

    return render(request, "users/sign_up.html", {'person_data': person_data})


@staff_member_required(login_url="users:login_not_staff")
def week_future_sign_ups(request):
    now = timezone.localtime()
    now_week_day = int(now.strftime("%w"))
    # 0 — воскресенье
    # 6 — суббота
    # вт ср чт пт сб вс пн
    # 2  3  4  5  6  0  1
    # пн — выходной
    now_week_day = now_week_day - 2 if now_week_day - 2 >= 0 else now_week_day + 5
    # вт ср чт пт сб вс пн
    # 0  1  2  3  4  5  6
    # 0 — вторник
    # 6 — понедельник
    # пн — выходной

    if now_week_day == 6:
        now = now + datetime.timedelta(days=1)
        now_week_day = 0

    day_previous_quantity = now_week_day
    day_next_quantity = abs(now_week_day - 6)

    now_week_dates = []

    for i in range(day_previous_quantity, 0, -1):
        now_week_dates.append(now.date() - datetime.timedelta(days=i))

    now_week_dates.append(now.date())

    for i in range(1, day_next_quantity + 1):
        now_week_dates.append(now.date() + datetime.timedelta(days=i))

    list_of_sign_ups_on_week = []
    for date in now_week_dates:
        list_of_sign_ups_on_week.append(PersonDataAndDate.objects.filter(date=date))

    dict_of_sign_ups_on_week = {
        "Вт": [now_week_dates[0], list_of_sign_ups_on_week[0]],
        "Ср": [now_week_dates[1], list_of_sign_ups_on_week[1]],
        "Чт": [now_week_dates[2], list_of_sign_ups_on_week[2]],
        "Пт": [now_week_dates[3], list_of_sign_ups_on_week[3]],
        "Сб": [now_week_dates[4], list_of_sign_ups_on_week[4]],
        "Вс": [now_week_dates[5], list_of_sign_ups_on_week[5]],
        "Пн": [now_week_dates[6], list_of_sign_ups_on_week[6]]
    }

    return render(request, "users/week_future_sign_ups.html", {"sign_ups": dict_of_sign_ups_on_week})


@staff_member_required(login_url="users:login_not_staff")
def ban_list(request):
    users = UserPlus.objects.filter(not_baned=False)
    users_baned = [u.user_id for u in users]
    return render(request, "users/ban_list.html", {"users": users_baned})


@csrf_exempt
@staff_member_required(login_url="users:login_not_staff")
def unban_user(request):
    pk = json.loads(request.body)
    u = get_user_model().objects.get(pk=pk)
    u.userplus.not_baned = True
    u.userplus.save()
    return JsonResponse({"success": True})


@staff_member_required(login_url="users:login_not_staff")
def unban_list(request):
    users = UserPlus.objects.filter(not_baned=True)
    users_unbaned = [u.user_id for u in users]
    return render(request, "users/unban_list.html", {"users": users_unbaned})


@csrf_exempt
@staff_member_required(login_url="users:login_not_staff")
def ban_user(request):
    pk = json.loads(request.body)
    u = get_user_model().objects.get(pk=pk)
    u.userplus.not_baned = False
    u.userplus.save()
    return JsonResponse({"success": True})