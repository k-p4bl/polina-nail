from django.contrib import admin

from .models import ServiceForHtml, AdditionalServiceForHtml


@admin.register(ServiceForHtml)
class ServiceForHtmlAdmin(admin.ModelAdmin):
    list_display = ['service', 'price', 'filming_work']


admin.site.register(AdditionalServiceForHtml)

