from django.shortcuts import render
from django.db.models import Q
from .models import Book
from accounts.models import Team

# Create your views here.
def index(request):
    login_user = request.user
    if login_user.username != '':
        available_teams = Team.objects.filter(members=login_user)
        available_items = Book.objects.filter(Q(owner=login_user)|Q(team__in=available_teams)).distinct()
    else:
        available_items = Team.objects.none()
        
    params = {
        'login_user' : login_user,
        'items': available_items,
    }
    return render(request, 'index.html', params)