from django.conf.urls.static import static
from django.urls import path

from nail_studio import settings
from . import views


urlpatterns = [
    path('', views.index, name='main_page'),
    path('privacy/', views.privacy, name='privacy'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
