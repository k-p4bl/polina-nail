from django.conf.urls.static import static
from django.urls import path

from nail_studio import settings
from . import views


urlpatterns = [
    path('', views.index, name='main_page'),
    path('privacy/', views.privacy, name='privacy'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('sign_up/finish/<int:pk>', views.sign_up_finish, name='sign_up_finish'),
    path('sign_up/create_calendar_event/', views.create_calendar_event, name='create_calendar_event'),
    path('sign_up/<service>/', views.sign_up, name='sign_up_with_args'),
    path('validate_date', views.validate_date, name='validate_date'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
