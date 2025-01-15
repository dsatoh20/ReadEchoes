from django.urls import path

from . import views
from django.urls import path, reverse_lazy

app_name = 'media_uploader'
urlpatterns = [
    path('', views.upload_static_media, name='index'),
]