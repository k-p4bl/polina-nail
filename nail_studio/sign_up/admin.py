from django.contrib import admin
from django.utils.timezone import localtime, localdate

from integrations.google.calendar.calendar_client import GoogleCalendar
from integrations.yookassa.payments import YandexPayment
from main_page.models import ServiceForHtml
from .forms import SignUpAdminForm
from .models import PersonDataAndDate, DisabledDates, Service, Time


@admin.register(PersonDataAndDate)
class PersonDataAdmin(admin.ModelAdmin):
    form = SignUpAdminForm
    list_display = ['last_name', 'phone_number', 'date', 'time', 'service']
    search_fields = ['last_name', 'phone_number']
    readonly_fields = ['payment_id']

    def save_model(self, request, obj, form, change):
        cd = form.cleaned_data
        calendar = GoogleCalendar()

        if change:
            description = (f"{form.initial['phone_number']} {form.initial['last_name']} {form.initial['first_name']} "
                           f"{form.initial['patronymic']}")
            event = calendar.get_event(description, form.initial['date'],
                                       Time.objects.get(pk=form.initial['time']).time)

            args = {'date': None,
                    'time': None,
                    'service': None,
                    'description': None,
                    'hour': None,
                    'minute': None}

            if 'last_name' in form.changed_data \
                    or 'first_name' in form.changed_data \
                    or 'patronymic' in form.changed_data \
                    or 'phone_number' in form.changed_data:
                args['description'] = f"{cd['phone_number']} {cd['last_name']} {cd['first_name']} {cd['patronymic']}"
            if 'service' in form.changed_data:
                args['service'] = cd['service'].service
                args['hour'], args['minute'] = ServiceForHtml.objects.get(service=args['service']).get_time_to_comp()
            if 'date' in form.changed_data:
                args['date'] = cd['date']
            if 'time' in form.changed_data:
                args['time'] = cd['time'].time

            event.change(*args.values())

            try:
                DisabledDates.objects.get(start_date=form.initial['date'], creator_is_human=False).delete()
            except DisabledDates.DoesNotExist:
                pass

            if PersonDataAndDate.objects.filter(date=cd['date']).count() >= Time.objects.count():
                DisabledDates.objects.create(start_date=cd['date'], creator_is_human=False)

        else:

            if PersonDataAndDate.objects.filter(date=cd['date']).count() >= Time.objects.count():
                DisabledDates.objects.create(start_date=cd['date'], creator_is_human=False)

            date = obj.date.strftime('%Y-%m-%d')
            time = obj.time.time
            service_for_calendar = obj.service.service
            description = (f"{obj.phone_number} "
                           f"{obj.last_name} "
                           f"{obj.first_name} "
                           f"{obj.patronymic}")
            h, m = ServiceForHtml.objects.get(service=service_for_calendar).get_time_to_comp()

            calendar.add_event(date=date, time=time, service=service_for_calendar, description=description, hour=h,
                               minute=m)
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj: PersonDataAndDate):
        if obj.payment_id:
            delta = obj.date - localdate()
            if delta.days >= 3:
                payment = YandexPayment()
                payment.refund_payment(obj.payment_id)

        calendar = GoogleCalendar()

        try:
            DisabledDates.objects.get(start_date=obj.date, creator_is_human=False).delete()
        except DisabledDates.DoesNotExist:
            pass
        description = f"{obj.phone_number} {obj.last_name} {obj.first_name} {obj.patronymic}"
        calendar.get_event(description, obj.date, obj.time.time).delete()
        super().delete_model(request, obj)


@admin.register(DisabledDates)
class DisabledDatesAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'finish_date', 'creator_is_human']
    readonly_fields = ['creator_is_human']


admin.site.register(Service)
admin.site.register(Time)
