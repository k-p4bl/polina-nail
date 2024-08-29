import datetime
import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from integrations.google.calendar.calendar_client import GoogleCalendar
from integrations.yookassa.payments import YandexPayment
from main_page.models import ServiceForHtml
from . import models
from django.views.decorators.csrf import csrf_exempt

from .forms import SignUpForm, SignUpErrorList
from .models import Time


def sign_up(request, service=None):
    """
        Собирает в список даты из базы данных, у которых 3 времени,
        и из таблицы отключенные даты, и отправляет в context.
        При post запросе создает экземпляр модели записи
        """
    list_of_date = models.DisabledDates.objects.get_disabled_dates()
    service_html = ServiceForHtml.objects.all()
    personal_data = {}

    if request.method == 'POST':
        form = SignUpForm(request.POST, error_class=SignUpErrorList)
        if form.is_valid():
            cd = form.cleaned_data

            data = {
                'user_is_auth': request.user.is_authenticated,
                'last_name': cd['person_name'][0],
                'first_name': cd['person_name'][1],
                'patronymic': cd['person_name'][2],
                'phone_number': cd['phone_number'],
                'year': int(cd['date'].strftime("%Y")),
                'month': int(cd['date'].strftime("%m")),
                'day': int(cd['date'].strftime("%d")),
                'time': cd['time'].pk,
                'service': cd['service'].pk,
                'add_services_id': cd['add_service']
            }
            response = {'data': data}
            if not request.user.is_authenticated or not request.user.userplus.not_baned:
                prepayment = ServiceForHtml.objects.get(service=cd['service'].service).prepayment

                person_name = f"{data['last_name']} {data['first_name']} {data['patronymic']}"

                payment = YandexPayment()
                payment_response = payment.create_payment(prepayment, cd['service'].service, data['phone_number'],
                                                          person_name, request.user.is_authenticated, request.user.pk)

                data['payment_id'] = payment_response.id
                confirmation_token = payment_response.confirmation.confirmation_token

                response['confirmation_token'] = confirmation_token

            return JsonResponse(response)

    else:
        if request.user.is_authenticated:
            person_name = (request.user.last_name + " " + request.user.first_name + " " +
                           request.user.userplus.patronymic)
            if request.user.username[1:2] == "7":
                phone_number = (request.user.username[:2] + " (" + request.user.username[2:5] + ") " +
                                request.user.username[5:8] + "-" + request.user.username[8:10] + "-" +
                                request.user.username[10:])
            else:
                phone_number = request.user.username

            personal_data['person_name'] = person_name
            personal_data['phone_number'] = phone_number

            form = SignUpForm(error_class=SignUpErrorList)
        else:
            form = SignUpForm(error_class=SignUpErrorList)

    context = {
        "data": personal_data,
        'dates': list_of_date,
        'service': service,
        'form': form,
        'ServiceForHtml': service_html,
    }

    return render(request, 'sign_up/record.html', context)


@csrf_exempt
def create_obj_of_sign_up(request):
    data = json.loads(request.body)
    date = datetime.date(data['year'], data['month'], data['day'])
    try:
        payment = data['payment_id']
    except KeyError:
        payment = None

    person_name = models.PersonDataAndDate.objects.create(
        last_name=data['last_name'],
        first_name=data['first_name'],
        patronymic=data['patronymic'],
        phone_number=data['phone_number'],
        date=date,
        time=models.Time.objects.get(pk=data['time']),
        service=models.Service.objects.get(pk=data['service']),
        payment_id=payment,
        user_id=request.user if request.user.is_authenticated else None
    )
    if models.PersonDataAndDate.objects.filter(date=date).count() >= models.Time.objects.count():
        models.DisabledDates.objects.create(start_date=date, creator_is_human=False)

    for service_id in data['add_services_id']:
        add_service = models.AdditionalService.objects.get(id=int(service_id))
        person_name.additional_service.add(add_service)

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
        times = Time.objects.all().count()
        res = {}
        for i in range(times):
            res[str(i)] = True
        return JsonResponse(res)
    year, month, day = date.split('-')
    select_day = datetime.date(int(year), int(month), int(day))

    times = Time.objects.all()
    response = {}
    s_ups = models.PersonDataAndDate.objects.filter(date=select_day)
    for i in range(times.count()):
        if s_ups:
            for s_up in s_ups:
                if s_up.time == times[i]:
                    response[str(i)] = True
                    break
                else:
                    response[str(i)] = False
        else:
            response[str(i)] = False

    # for s_up in models.PersonDataAndDate.objects.filter(date=select_day):
    #     response[str(s_up.time.pk)] = True

    return JsonResponse(response)


def get_additional_service(request):
    add_services = models.AdditionalService.objects.all()
    response = {}
    for service in add_services:
        response[str(service.pk)] = service.add_service
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
    additional_services = person_name.additional_service.all()
    calendar = GoogleCalendar()
    date = person_name.date.strftime('%Y-%m-%d')
    time = person_name.time.time
    service_for_calendar = person_name.service.service
    description = (
        f"{person_name.phone_number} "
        f"{person_name.last_name} "
        f"{person_name.first_name} "
        f"{person_name.patronymic}"
    )

    h, m = ServiceForHtml.objects.get(service=service_for_calendar).get_time_to_comp()

    if additional_services:
        for service in additional_services:
            service_for_calendar += f'\n\t+{service}'

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
