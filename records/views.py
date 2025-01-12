from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from records.forms import BookForm
from .models import Book, Like
from accounts.models import User, Team


# Create your views here.
def index(request):
    login_user = request.user
        
    params = {
        'login_user' : login_user,
        'items': get_available_items(login_user),
        'liked_items': get_liked_items(login_user),
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

def like(request, book_id):
    # likeボタン押下で作動
    login_user = request.user
    book = Book.objects.get(id=book_id)
    like = Like.objects.filter(owner=login_user).filter(book=book).first()
    if like:
        like.delete() # likeオブジェクトを削除
        book.good_count -= 1 # イイネ数を-1
        messages.debug(request, f'Removed like to {book}.')
    else:
        like = Like() # 新たにlikeオブジェクトを登録
        like.owner = login_user
        like.book = book
        like.save()
        book.good_count += 1 # イイネ数を+1
        messages.debug(request, f'Liked {book}.')
    book.save()
    referer_url = request.META.get('HTTP_REFERER', '/')
    print(referer_url)
    return HttpResponseRedirect(referer_url)

def record(request, book_id):
    login_user = request.user
    record = Book.objects.get(id=book_id)
    params = {
        'login_user': login_user,
        'item': record,
        'liked_items': get_liked_items(login_user)
    }
    return render(request, 'records/record.html', params)

@login_required
def portfolio(request):
    login_user = request.user
    items = Book.objects.filter(owner=login_user) if login_user.username != '' else Book.objects.none()
    params = {
        'login_user': login_user,
        'items': items,
        'liked_items': get_liked_items(login_user)
    }
    return render(request, 'records/portfolio.html', params)



"""
ただの関数below
"""
def get_available_items(user):
    if user.username != '':
        available_teams = Team.objects.filter(members=user).distinct()
        available_items = Book.objects.filter(Q(owner=user)|Q(team__in=available_teams)).distinct()
    else:
        available_items = Book.objects.none()
    return available_items

def get_liked_items(user):
    if user.username != '':
        available_teams = Team.objects.filter(members=user).distinct()
        likes = user.like_owner.all()
        liked_items = Book.objects.filter(Q(owner=user)|Q(team__in=available_teams)).filter(like_book__in=likes).distinct()
    else:
        liked_items = Book.objects.none()
    return liked_items