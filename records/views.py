from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from records.forms import BookForm
from .models import Book
from accounts.models import User
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

@login_required
def post(request):
    login_user = request.user
    if request.method == 'POST':
        form = BookForm(request.POST, login_user)
        if form.is_valid():
            book = form.save(commit=False)
            try:
                book.auto_fill()
                print('successfully complemented!')
            except Exception as e:
                print(f'failed to auto_fill...Err: {e}')
                messages.warning(request, 'Failed to get book information...please edit it manually.')
            book.owner = login_user
            book.save()
            if book.img_path == '':
                book.img_path = '/media/logo256.png'
                messages.debug(request, 'set logo as image_path.')
            messages.success(request, 'Successfully posted a new record!')
            return redirect('/')
        else:
            print(form.errors)
    else:
        form = BookForm(user=login_user)
    params = {
        'login_user': login_user,
        'form': form,
    }
    return render(request, 'records/post.html', params)