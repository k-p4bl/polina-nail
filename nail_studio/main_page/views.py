import json
import datetime

from django.http import JsonResponse
from django.shortcuts import render

from . import models
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    context = {
        'additional_services': models.AdditionalServiceForHtml.objects.all(),
        'services': models.ServiceForHtml.objects.all()
    }
    return render(request, 'main_page/index.html', context)


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


def privacy(request):
    return render(request, 'main_page/conf.html')
