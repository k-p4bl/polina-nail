from django.conf.urls.static import static
from django.urls import path

from nail_studio import settings
from . import views


urlpatterns = [
    path('', views.index, name='main_page'),
    path('privacy/', views.privacy, name='privacy'),
    path('validate_date/', views.validate_date, name='validate_date'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
