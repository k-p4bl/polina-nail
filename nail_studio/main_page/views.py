import json
import datetime

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.template import loader

from . import models
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def index(request):
    context = {
        'additional_services': models.AdditionalServiceForHtml.objects.all(),
        'services': models.ServiceForHtml.objects.all()
    }
    return render(request, 'main_page/index.html', context)


def privacy(request):
    return render(request, 'main_page/conf.html')


def bad_request(request, exception):
    return HttpResponseBadRequest(loader.render_to_string('main_page/bad_request.html',
                                                          {'exception': exception},
                                                          request))


def manual_user(request):
    return render(request, 'main_page/manual_user.html')
