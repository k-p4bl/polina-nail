import datetime
import json

from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from integrations.google.calendar.calendar_client import GoogleCalendar
from integrations.yookassa.payments import YandexPayment
from main_page.models import ServiceForHtml
from . import models
from django.views.decorators.csrf import csrf_exempt

from .forms import SignUpForm, SignUpErrorList


def sign_up(request, service=None):
    """
        Собирает в список даты из базы данных, у которых 3 времени,
        и из таблицы отключенные даты, и отправляет в context.
        При post запросе создает экземпляр модели записи
        """
    list_of_date = models.DisabledDates.objects.get_disabled_dates()
    service_html = ServiceForHtml.objects.all()
    if request.method == 'POST':
        form = SignUpForm(request.POST, error_class=SignUpErrorList)
        if form.is_valid():
            cd = form.cleaned_data

            data = {
                'last_name': cd['person_name'][0],
                'first_name': cd['person_name'][1],
                'patronymic': cd['person_name'][2],
                'phone_number': cd['phone_number'],
                'year': cd['date'].strftime("%Y"),
                'month': cd['date'].strftime("%m"),
                'day': cd['date'].strftime("%d"),
                'time': cd['time'].pk,
                'service': cd['service']
            }

            prepayment = ServiceForHtml.objects.get(service=data['service'].service).prepayment

            person_name = f'{data['last_name']} {data['first_name']} {data['patronymic']}'

            payment = YandexPayment()
            payment_response = payment.create_payment(prepayment, data['service'].service, data['phone_number'],
                                                      person_name, request.user.is_authenticated, request.user.pk)

            data['payment_id'] = payment_response.id
            confirmation_token = payment_response.confirmation.confirmation_token

        else:
            data = None
            confirmation_token = None

    else:
        form = SignUpForm(error_class=SignUpErrorList)
        data = None
        confirmation_token = None

    context = {
        'dates': list_of_date,
        'service': service,
        'form': form,
        'ServiceForHtml': service_html,
        'data': data,
        'confirmation_token': confirmation_token
    }

    return render(request, 'sign_up/record.html', context)


@csrf_exempt
def create_obj_of_sign_up(request):
    data = json.loads(request.body)
    date = datetime.date(data['year'], data['month'], data['day'])

    person_name = models.PersonDataAndDate.objects.create(last_name=data['last_name'],
                                                          first_name=data['first_name'],
                                                          patronymic=data['patronymic'],
                                                          phone_number=data['phone_number'],
                                                          date=date,
                                                          time=models.Time.objects.get(pk=data['time']),
                                                          service=models.Service.objects.get(pk=data['service']),
                                                          payment_id=data['payment_id']
                                                          )
    if models.PersonDataAndDate.objects.filter(date=date).count() >= models.Time.objects.count():
        models.DisabledDates.objects.create(start_date=date, creator_is_human=False)

    return JsonResponse({'pk': str(person_name.pk)})


@csrf_exempt
def validate_date(request):
    """
    При нажатии на день в календаре приходит дата в формате json
    При повторном нажатии на день запрос приходит, но без даты
    Эта функция, при отсутствии даты, возвращает json со словарем, в котором
    время(строка) и булево значение (все в True)(True - время занято, False - нет).
    Если дата есть, то функция запрашивает данную дату из базы данных, если такая имеется,
    то она ставит значения в True тому времени, которое находит
    """
    # Приходит дата с js в формате json (ГГГГ-ММ-ДД)
    date = json.loads(request.body)
    # Проверка на то, есть ли дата в запросе
    try:
        date = date[0]
    # Если даты нет, то отправляю объект, который деактивирует все кнопки
    except IndexError:
        return JsonResponse({'10': True, '13': True, '16': True, })
    year, month, day = date.split('-')
    select_day = datetime.date(int(year), int(month), int(day))
    # Создаю словарь со значениями по умолчанию (все кнопки активны)
    response = {'10': False,
                '13': False,
                '16': False,
                }

    for t in models.PersonDataAndDate.objects.filter(date=select_day):
        t = t.time.time.strftime('%H')
        response[t] = True

    return JsonResponse(response)


def sign_up_finish(request, pk):
    person_name = models.PersonDataAndDate.objects.get(pk=pk)
    date = person_name.date.strftime('%d.%m')
    time = person_name.time.time.strftime('%H:%M')
    context = {
        'pk': pk,
        'date': date,
        'time': time,
        'name': person_name.first_name
    }
    return render(request, 'sign_up/record_finish.html', context)


@csrf_exempt
def create_calendar_event(request):
    pk = json.loads(request.body)

    person_name = models.PersonDataAndDate.objects.get(pk=pk)
    calendar = GoogleCalendar()
    date = person_name.date.strftime('%Y-%m-%d')
    time = person_name.time.time
    service_for_calendar = person_name.service.service
    description = (f"{person_name.phone_number} "
                   f"{person_name.last_name} "
                   f"{person_name.first_name} "
                   f"{person_name.patronymic}")
    h, m = ServiceForHtml.objects.get(service=service_for_calendar).get_time_to_comp()

    calendar.add_event(date=date, time=time, service=service_for_calendar, description=description, hour=h, minute=m)

    return HttpResponse(status=200)


def sign_up_error(request):
    return render(request, 'sign_up/error.html')


def delete_obj_of_sign_up(request, pk):
    try:
        models.PersonDataAndDate.objects.get(pk=pk).delete()
    except:
        return HttpResponse(status=400)
    else:
        return HttpResponse(status=200)
