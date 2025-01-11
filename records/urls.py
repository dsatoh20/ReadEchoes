from django.urls import path

from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

app_name = 'records'
urlpatterns = [
    path('', views.index, name='index'),
    path('post', views.post, name='post'),
]
