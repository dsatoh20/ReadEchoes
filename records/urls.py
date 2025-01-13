from django.urls import path

from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

app_name = 'records'
urlpatterns = [
    path('', views.index, name='index'),
    path('post', views.post, name='post'),
    path('like/<int:book_id>', views.like, name='like'),
    path('record/<int:book_id>', views.record, name='record'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('record/<int:book_id>/reply/<comment_id>', views.reply, name='reply'),
]
