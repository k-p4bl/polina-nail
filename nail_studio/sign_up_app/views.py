from django.contrib.auth.decorators import permission_required, login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from main_page.models import PersonName, Service, Date


@login_required
@permission_required(
    perm=['main_page.add_personname', 'main_page.change_personname', 'main_page.delete_personname'],
    raise_exception=True
)
def sign_up_app(request):
    search_query = request.GET.get('search', '')
    date = Date.objects.filter(date__gte=timezone.localdate())

    if search_query:
        service = Service.objects.filter(service__icontains=search_query)
        sign_ups = PersonName.objects.filter(Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query) | Q(service__in=service), Q(date__in=date))
    else:
        sign_ups = PersonName.objects.filter(date__in=date)

    return render(request, 'sign_up_app/sign_ups.html', {'sign_ups': sign_ups})


@login_required
@permission_required(perm='main_page.add_personname', raise_exception=True)
def add(request):
    return render(request, 'sign_up_app/add.html')


@login_required
@permission_required(perm=['main_page.change_personname', 'main_page.delete_personname'], raise_exception=True)
def choice(request, pk):
    last_name = PersonName.objects.get(pk=pk).last_name
    return render(request, 'sign_up_app/choice.html', {'last_name': last_name, 'pk': pk})


# TODO Сделать форму, чтобы редактировать запись
@login_required
@permission_required(perm='main_page.change_personname', raise_exception=True)
def change(request, pk):
    return render(request, 'sign_up_app/change.html')


# TODO Реализовать удаление записи и разрыв даты в времени
@login_required
@permission_required(perm='main_page.delete_personname', raise_exception=True)
def delete(request):
    return render(request, 'sign_up_app/delete.html')

