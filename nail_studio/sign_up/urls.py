from django.conf.urls.static import static
from django.urls import path

from nail_studio import settings
from . import views

urlpatterns = [
    path('', views.sign_up, name='sign_up'),
    path('validate_date/', views.validate_date, name='validate_date'),
    path('create_obj_of_sign_up/', views.create_obj_of_sign_up, name='create_obj_of_sign_up'),
    path('finish/<int:pk>/', views.sign_up_finish, name='sign_up_finish'),
    path('error/', views.sign_up_error, name='sign_up_error'),
    path('delete_obj_of_sign_up/<int:pk>/', views.delete_obj_of_sign_up, name='delete_obj_of_sign_up'),
    path('create_calendar_event/', views.create_calendar_event, name='create_calendar_event'),
    path('<service>/', views.sign_up, name='sign_up_with_args'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
