from django.contrib import admin

from .models import PersonName, ServiceForHtml, Service, Date, Time, DisabledDates, AdditionalServiceForHtml


@admin.register(PersonName)
class PersonNameAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'phone_number', 'date', 'time', 'service']
    search_fields = ['last_name', 'phone_number', 'date__date']


class PersonNameInLine(admin.StackedInline):
    model = PersonName
    extra = 0


@admin.register(Date)
class DateAdmin(admin.ModelAdmin):
    inlines = [PersonNameInLine]


@admin.register(ServiceForHtml)
class ServiceForHtmlAdmin(admin.ModelAdmin):
    list_display = ['service', 'price', 'filming_work']


@admin.register(DisabledDates)
class DisabledDatesAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'finish_date']


admin.site.register(AdditionalServiceForHtml)
admin.site.register(Service)
admin.site.register(Time)
