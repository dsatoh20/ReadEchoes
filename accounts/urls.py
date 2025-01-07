from django.urls import path

from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('accounts:login')), name='logout'),
    path('team/', views.team, name='team'),
    path('createteam/', views.createteam, name='createteam'),
]