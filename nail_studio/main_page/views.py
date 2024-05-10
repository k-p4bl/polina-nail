import json
import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect

from integrations.google.calendar.calendar_client import GoogleCalendar
from . import models
from django.views.decorators.csrf import csrf_exempt

from .forms import SignUpForm, SignUpErrorList
from .models import AdditionalServiceForHtml


# Create your views here.
def index(request):
    context = {
        'additional_services': AdditionalServiceForHtml.objects.all(),
        'services': models.ServiceForHtml.objects.all()
    }
    return render(request, 'main_page/index.html', context)


# Проверить правильные даты ли собраны
def sign_up(request, service=None):
    """
    Собирает в список даты из базы данных, у которых 3 времени,
    и из таблицы отключенные даты, и отправляет в context.
    При post запросе создает экземпляр модели записи
    """
    list_of_date = models.Date.objects.get_dates_with_three_times()
    list_of_date += models.DisabledDates.objects.get_disabled_dates()
    service_html = models.ServiceForHtml.objects.all()
    if request.method == 'POST':
        form = SignUpForm(request.POST, error_class=SignUpErrorList)
        if form.is_valid():
            form.cleaned_data['time'].date_set.add(form.cleaned_data['date'][0])
            person_name = models.PersonName.objects.create(last_name=form.cleaned_data['person_name'][0],
                                                           first_name=form.cleaned_data['person_name'][1],
                                                           patronymic=form.cleaned_data['person_name'][2],
                                                           phone_number=form.cleaned_data['phone_number'],
                                                           date=form.cleaned_data['date'][0],
                                                           time=form.cleaned_data['time'],
                                                           service=form.cleaned_data['service']
                                                           )

            return redirect('sign_up_finish', person_name.pk, permanent=True)

    else:
        form = SignUpForm(error_class=SignUpErrorList)

    context = {'dates': list_of_date,
               'service': service,
               'form': form,
               'ServiceForHtml': service_html
               }

    return render(request, 'main_page/record.html', context)


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
    try:
        date = models.Date.objects.get(date=select_day)
        list_of_time = date.time.all()
    except models.Date.DoesNotExist:
        list_of_time = []

    for t in list_of_time:
        t = t.time.strftime('%H')
        response[t] = True

    return JsonResponse(response)


def sign_up_finish(request, pk):
    return render(request, 'main_page/record_finish.html', {'pk': pk})


@csrf_exempt
def create_calendar_event(request):
    pk = json.loads(request.body)

    person_name = models.PersonName.objects.get(pk=pk)
    calendar = GoogleCalendar()
    date = person_name.date.date.strftime('%Y-%m-%d')
    time = person_name.time.time
    service_for_calendar = person_name.service.service
    description = (f"{person_name.phone_number} "
                   f"{person_name.last_name} "
                   f"{person_name.first_name} "
                   f"{person_name.patronymic}")
    h, m = models.ServiceForHtml.objects.get(service=service_for_calendar).get_time_to_comp()

    calendar.add_event(date=date, time=time, service=service_for_calendar, description=description, hour=h, minute=m)

    return JsonResponse({'success': True})


def privacy(request):
    return render(request, 'main_page/conf.html')

