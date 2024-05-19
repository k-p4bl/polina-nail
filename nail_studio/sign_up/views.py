import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from integrations.google.calendar.calendar_client import GoogleCalendar
from integrations.yookassa.payments import YandexPayment
from main_page import models
from django.views.decorators.csrf import csrf_exempt

from .forms import SignUpForm, SignUpErrorList


# Create your views here.
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
            cd = form.cleaned_data

            cd['time'].date_set.add(cd['date'][0])
            person_name = models.PersonName.objects.create(last_name=cd['person_name'][0],
                                                           first_name=cd['person_name'][1],
                                                           patronymic=cd['person_name'][2],
                                                           phone_number=cd['phone_number'],
                                                           date=cd['date'][0],
                                                           time=cd['time'],
                                                           service=cd['service']
                                                           )

            return redirect('step_for_payment', person_name.pk, permanent=True)
    else:
        form = SignUpForm(error_class=SignUpErrorList)

    context = {'dates': list_of_date,
               'service': service,
               'form': form,
               'ServiceForHtml': service_html
               }

    return render(request, 'sign_up/record.html', context)


def payments(request, pk):

    person = models.PersonName.objects.get(pk=pk)
    prepayment = models.ServiceForHtml.objects.get(service=person.service.service).prepayment

    payment = YandexPayment()
    payment_response = payment.create_payment(prepayment, person.service.service, person.phone_number)

    context = {
        'pk': pk,
        'confirmation_token': payment_response.confirmation.confirmation_token
    }
    return render(request, 'sign_up/payment.html', context)


def step_for_payment(request, pk):
    return render(request, 'sign_up/step_for_payment.html', {'pk': pk})


def sign_up_finish(request, pk):
    person_name = models.PersonName.objects.get(pk=pk)
    date = person_name.date.date.strftime('%d.%m')
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

    return HttpResponse(status=200)


def sign_up_error(request, pk):
    person = models.PersonName.objects.get(pk=pk)
    person.time.date_set.remove(person.date)
    person.delete()

    return render(request, 'sign_up/error.html')
