from django.urls import path
from . import views


urlpatterns = [
    path('', views.sign_up_app, name='sign_up_app'),
    path('choice/<int:pk>', views.choice, name='choice'),
    path('add/', views.add, name='add'),
    path('change/<int:pk>', views.change, name='change'),
    path('delete/<int:pk>', views.delete, name='delete'),
]