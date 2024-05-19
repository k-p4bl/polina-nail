from django.conf.urls.static import static
from django.urls import path

from nail_studio import settings
from . import views

urlpatterns = [
    path('', views.sign_up, name='sign_up'),
    path('step_for_payment/<int:pk>/', views.step_for_payment, name='step_for_payment'),
    path('payment/<int:pk>/', views.payments, name='payment'),
    path('finish/<int:pk>/', views.sign_up_finish, name='sign_up_finish'),
    path('error/<int:pk>/', views.sign_up_error, name='sign_up_error'),
    path('create_calendar_event/', views.create_calendar_event, name='create_calendar_event'),
    path('<service>/', views.sign_up, name='sign_up_with_args'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
